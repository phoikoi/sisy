Data migrations
===============

When creating applications that use Sisy to maintain various regular housekeeping
tasks, it can be handy to have those tasks automatically created on installation,
rather than having to manually create them in the admin interface.  This can be
accomplished by creating a *data migration* within the application's ``migrations``
directory.  This will be applied by the Django ``migrate`` command.

It's worth a read through the
`Django documentation on data migrations <https://docs.djangoproject.com/en/1.11/topics/migrations/#data-migrations>`_
if you haven't created one before.

For use with Sisy tasks, the migration file could look similar to the following:

..  code-block:: python

    from django.db import migrations
    from myapp.utilities import daily_maintenance
    from sisy.models import task_with_callable

    TASK_NAME = 'Daily data maintenance'

    def add_repeating(apps, schema_editor):
        task = task_with_callable(
            daily_maintenance,
            label=TASK_NAME,
            schedule='30 0 * * *', # every day at 30 minutes past midnight
            userdata={}, # optional
        )
        task.save()

    def remove_repeating(apps, schema_editor):
        Task = apps.get_model('sisy.Task')
        task = Task.objects.get(label=TASK_NAME)
        task.delete()

    class Migration(migrations.Migration):
        dependencies = [
            ('myapp', '0001_initial'),
            ('sisy', '0001_initial'),
        ]
        operations = [
            migrations.RunPython(add_repeating, reverse_code=remove_repeating)
        ]


The dependencies will of course have to be adjusted to fit your app's state,
but in any case, the dependency on the latest Sisy migration file needs to
be there.  At the time of writing, there is only one, but after the package
is released to the public, it may change.

Instance methods in data migrations
-----------------------------------

The example given above will work just fine with plain functions, and with class methods and static
methods of classes that are not Django models. But when it comes to instance methods, things get sticky.
Instance methods are only useful if you have an instance of the class to work with, and the remote
worker process that the task will be run on has no way of getting to the object instance that the
migration is working with.

Of course, Django model classes are designed to carry their state and be "reanimated", if you will,
but in the case of migrations they have their own problems.  Migrations are exactly the process of
changing the Django models in some way or other, and as a consequence, the models we can access
during the migration process have no methods at all--not instance, class, or static methods.  So
in a migration file, we cannot send our method callables to :py:func:`task_with_callable` as actual objects.
We must use a dotted path.

In the case of instance methods, there is an additional wrinkle. With class and static methods,
the dotted path is sufficient to completely specify the identity of the function to run.  However,
with instance methods, we also need to know which instance should be associated with the function.
For this specific case, there is an additional argument to :py:func:`task_with_callable`: ``pk_override``.
This argument takes the integer PK (primary key) ID of the Django model instance that should be retrieved
when the function will be run:

.. code-block:: python

    from django.db import migrations
    from sisy.models import task_with_callable, taskinfo_with_label

    TASK_NAME = 'A suitably unique label for the task'
    METHOD_NAME = 'myapp.models.ModelFoo.InstanceMethod'

    # Function to run the forward migration
    def add_repeating(apps, schema_editor):
        # Look up our model by asking Django for it
        # This is only a stand-in class, not the real thing
        ModelFoo = apps.get_model('myapp.ModelFoo')
        # Create a new instance of our class
        newFoo = ModelFoo()
        # We must save the object to set its PK.
        # Note: there are no custom methods at this point;
        # including overridden save() methods!
        newFoo.save()

        task = task_with_callable(
            newFoo.InstanceMethod,
            label=TASK_NAME,
            schedule='* * * * *',
            pk_override=newFoo.pk,
        )
        task.save()

    # Function to run the reverse migration
    def remove_repeating(apps, schema_editor):
        # Get the temporary version of sisy.Task
        Task = apps.get_model('sisy.Task')
        # Get the temporary version of our model class
        ModelFoo = apps.get_model('myapp.ModelFoo')

        # Look up our task by label
        task = Task.objects.get(label=TASK_NAME)
        # Disable it so it can't have a race condition while
        # we're removing it (unless it's already running, which
        # is another problem entirely)
        task.enabled=False
        task.save()

        # Look up our callable object's task info with a special function
        # and pull the object's PK out of it
        oldFooPK = taskinfo_with_label(TASK_NAME)['model_pk']

        # Retrieve the object and delete it
        # This is not mandatory, but probably a good idea.
        oldFoo = ModelFoo.objects.get(pk=oldFooPK)
        oldFoo.delete()

        # Now we can delete the task object.
        task.delete()

    class Migration(migrations.Migration):
        # You must adapt the dependencies to fit your own project's
        # existing migrations. This example is from the demo project.
        dependencies = [
            ('myapp', '0004-setup-staticmethod-task'),
            ('sisy', '0001_initial'),
        ]
        operations = [
            migrations.RunPython(add_repeating, reverse_code=remove_repeating)
        ]

