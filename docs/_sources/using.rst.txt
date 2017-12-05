.. _using-sisy:

Using Sisy
==========

Quick overview of Sisy's architecture
-------------------------------------

Task objects
++++++++++++

The heart of Sisy is the :py:class:`sisy.models.Task` model class, whose instances
embody and keep track of the tasks that Sisy will (attempt to) run on your behalf.
The class allows a variety of different ways to schedule task execution, using its
various fields.

Task functions
++++++++++++++

Each task ultimately runs a function that you provide, which takes one argument.
This argument, which must be named ``message``, receives a ``dict`` object with
two keys: ``task``, and ``message``.  The value of the ``task`` key is the
:py:class:`Task` object administrating the current task run, and the ``message``
object is the message dictionary received by the Channels consumer function on the
current worker, which kicked off the execution of the task run.

Heartbeat worker
++++++++++++++++

The sisy package has a long-lived management command named ``sisy_heartbeat``, which
provides the periodic "heartbeat" messages that allow Sisy to do its job.  This management
command does not daemonize itself; therefore it can easily be run as a `supervisor <http://supervisord.org/>`_
program or a `honcho <https://github.com/nickstenning/honcho>`_ process.  The author usually
runs the heartbeat command on the same physical hardware as the ``daphne`` interface server,
since the heartbeat command takes very little resources and may be considered as
application-wide infrastructure, like the interface server.  There only needs to be one
heartbeat worker across the entire application.

Storing user data in the task object
++++++++++++++++++++++++++++++++++++

:py:class:`Task` objects have a property named ``userdata``, which is a :py:class:`dict`
object of JSON-serializable data.  Sisy does not do anything with this object; it is
there for the user to store application data.  The data is automatically encoded and
decoded to and from the :py:class:`Task` object's ``_extra_data`` field, and so is
available to task functions when they run, both for reading and writing.  It is best
to limit the size of data stored in this field, as the JSON is encoded/decoded on
each access, and so there might be a significant performance and/or memory penalty
incurred if the data is too large.

Creating and running tasks
--------------------------

:py:func:`sisy.models.task_with_callable`
+++++++++++++++++++++++++++++++++++++++++

This helper function is the standard way of creating a task, since creating the
detailed information that the Task object needs (from scratch, via the constructor
method) can be tedious.

The basic form of creating and running a Sisy :py:class:`Task` is the following:

.. code-block:: python

    from sisy.models import task_with_callable

    def my_task_function(message):
        do_something_here()

    task = task_with_callable(my_task_function)

    # Run the task every five seconds, but only during the hours
    # of midnight, 3am, 6am, and 9am.
    task.schedule = '*/5 0,3,6,9 * * *'
    task.save()

This is only the most basic form, but is the recommended method.  The
:py:func:`sisy.models.task_with_callable` method is the most convenient way to start
a task that has already been directly linked to a function. But you can
also specify the various parameters directly in the constructor.

The callable object that is passed to :py:func:`sisy.models.task_with_callable` can be specified as
an actual callable object, or as a string representing the full dotted Python path
to the callable object.

The callable object *must* take only one parameter, which must be named ``message``.
This parameter will receive a dictionary containing two keys: ``task``, and ``message``,
whose values are (respectively) the :py:class:`Task` object for this task, and the Channels message dictionary
that was received by the consumer function on the worker process.

Helper functions
++++++++++++++++

There are also a few helper functions in the :py:mod:`sisy.models` module that
make common scenarios easier to use.

:py:meth:`sisy.models.Task.run_iterations`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This helper class function allows the developer to specify that the task should run
a given number of times, and then be deleted.

:py:meth:`sisy.models.Task.run_once`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This helper class function allows the developer to specify that the task should run
once, immediately, and then be deleted.

What can be a task function?
----------------------------

There are several types of callables that are supported by Sisy:

* bare functions
* class methods
* static methods
* instance methods

The first three types are fairly simple; just pass the object or the dotted-path
string to :py:func:`task_with_callable`, and the task will be created. The
:py:class:`Task` object is passed back to you, so that you can adjust its settings
if desired.  You need to :py:meth:`save()` the object before it will become active.

.. code-block:: python

    from sisy.models import task_with_callable

    class Foo:
        @classmethod
        def DoSomethingClassy(cls, message):
            pass

    task = task_with_callable(Foo.DoSomethingClassy)
    # Set it to run during business hours on weekdays, once an hour on the hour
    task.schedule = '0 9-17 * * mon-fri'
    task.save()


Instance methods, however, are somewhat more complicated because of the
fact that they can only be called when they are bound to a specific
instance.  Because Sisy's tasks can be run on any worker process (potentially on
completely different hardware and even a different platform,) we cannot know what
the internal state of an object instance is, in order to run it on that remote worker.
The only case where this state can be reliably available to us is with our Django model objects,
and so those objects are the only ones on which Sisy supports calling instance methods:

.. code-block:: python

    from django.db import models
    from django.utils import timezone

    # Import our creation function
    from sisy.models import task_with_callable

    class ModelFoo(models.Model):
        """A very silly example model class"""
        name = models.CharField(max_length=127)
        latest_run = models.DateTimeField(null=True)

        def doSomething(self, message):
            """Do something very noddy, just for an example"""
            self.latest_run = timezone.now()
            self.save()


    def create_task_for_a_ModelFoo():
        """Create a Sisy task for the first ModelFoo we can grab"""

        # Grab the first ModelFoo in the list
        a_foo = ModelFoo.objects.all()[0]

        # Make a task with that ModelFoo's doSomething instance method
        task = task_with_callable(a_foo.doSomething)

        # Set it to run every five minutes
        task.schedule = '*/5 * * * *'

        # Save the task to activate it
        task.save()

The preceding (silly) example will create a task that runs every five minutes, calling
the ``doSomething`` method on the ``ModelFoo`` object that was retrieved in the
``create_task_for_a_ModelFoo`` function.


Execution options
-----------------

.. _repeating-tasks:

Repeating tasks
+++++++++++++++

The original intent of Sisy (evidenced by the choice of name, referencing
the tragic figure of `Sisyphus <https://en.wikipedia.org/wiki/Sisyphus>`_)
was to make it easy to run repeating tasks in background workers, much like
the classic Unix*cron* utility.  In fact, Sisy uses the same basic syntax as *cron*:

The schedule string is divided into five (or, optionally, six) fields
denoting different spans of time:

===== ============ ================================
field time period  Ranges
----- ------------ --------------------------------
  1   minutes      \*, 0-59, \*/x, x-y, x,y,z...
  2   hours        \*, 0-23, \*/x, x-y, x,y,z...
  3   day of month \*, 0-31, \*/x, x-y, "l" (for Last), x,y,z...
  4   month        \*, 1-12, \*/x, x-y, x,y,z...
  5   day of week  \*, 0-7 (both 0 and 7 are Sunday), "mon" - "sun"
  6\*  seconds      \*, 0-59, \*/x, x-y, x,y,z...
===== ============ ================================

*\*Field 6 is an extension, not supported by basic cron.*

Each field supports various forms of specification; some are common to all
of the fields, but some are field-specific.

Common formats
^^^^^^^^^^^^^^

\*
    Denotes "all" or "every".  Will allow the task to run at any value of the field.
\*/x
    Denotes "every *x*", such as ``*/5 * * * *`` for "every 5 minutes."
x-y
    Denotes a span of values (e.g. "0-7" or "mon-fri".)
x,y
    Denotes a series of values (e.g. ``0,5,20,25 * * * *``)
x\ :sub:`1`-y\ :sub:`1`,\ x\ :sub:`2`-y\ :sub:`2`
    Denotes a combination of the above specs; a series of spans of values (e.g. ``0-10,20-30 * * * *``)

Field-specific formats
^^^^^^^^^^^^^^^^^^^^^^

Day of month (field 3)
    Supports the use of "l" (lowercase L) to denote the "l"ast day of the month
Day of week (field 5)
    If a numeric spec is used, both ``0`` and ``7`` may be used to denote Sunday. Also,
    the abbreviated (English) text names of the days may be used: ``mon``, ``tue``,
    ``wed``, ``thu``, ``fri``, ``sat``, ``sun``.

Combining the formats
^^^^^^^^^^^^^^^^^^^^^

The power of the format comes from combining the different fields in different
specifications.  Some examples:

``"* * * * *"``
    This is the most basic specification (and the default), which would match any time.
    By default, Sisy runs its heartbeat process once per minute, so this spec would
    run once per minute.  This matches the behavior of the Unix *cron* utility.

``"30 0 * * *"``
    This specification would cause the task to be run at 00:30 (30 minutes
    after midnight) on every day of the month, in every month, on any day
    of the week.

``"*/5 * * * *"``
    This spec would run every five minutes, on all days, at all hours. The
    ``*/x`` form indicates "every *x*".

``"0-10,15-20 * * * *"``
    This spec would run on minutes 0 through 10 and 15 through 20 of every
    hour of every day.

``0,15,30,45 9-17 * * mon-fri``
    This spec would run every fifteen minutes, from 9am to 5pm on Monday through Friday.

For further reference on the format, see
the documentation for `croniter <https://pypi.python.org/pypi/croniter>`_,
the Python package which Sisy relies on to process it, or search Google for
something like *"crontab format"*.

.. _start-and-end-dates:

Start and end dates
+++++++++++++++++++

Start and end dates can be specified for a task, and the task runner will
pay attention to these, not running any task whose start and end dates are
after or before the current time respectively.  If a task completes a run
and its next run would be scheduled after the specified end date, the
task will be submitted for deletion.

..  code-block:: python

    from django.utils.timezone import datetime, get_current_timezone
    from sisy.models import task_with_callable
    from myapp.utils import limited_time_offer_function

    TZ = get_current_timezone()

    task = task_with_callable(
        limited_time_offer_function,
        schedule='0 7-19 * * *', # only run 7am - 7pm
        start_running=datetime(2018,1,1, 0,0, tz=TZ), # first run would be New Year's Day, 0:00 local time
        end_running=datetime(2018,2,14, 0,0, tz=TZ), # last run would be 7pm local time on Feb. 13th
    )
    task.save()

.. _specified-iteration-counts:

Specified iteration counts
++++++++++++++++++++++++++

Tasks can also be specified with an iteration count, in order to limit the
number of times the task will be run.  The task still runs according to the
``schedule`` attribute of the task object, but will be deleted after the
specified number of runs (whether successful or not.)

.. note::

    In the case of an ambiguity between the iteration count and the end date,
    the end date will take priority, and the task will be deleted if that
    end date will occur before the task's next scheduled run, even if the
    iteration count is still above zero.

..  code-block:: python

    from sisy.models import Task
    from myapp.utils import first_ten_customers_function

    task = Task.run_iterations(
        first_ten_customers_function,
        schedule='0 7-19 * * *', # only run 7am - 7pm
        iterations=10,
    )


.. _one-shot-task-runs:

One-shot task runs
++++++++++++++++++

As a special case of :ref:`specified iteration counts <specified-iteration-counts>`,
Sisy can be called in a one-shot mode by using the :py:meth:`sisy.models.Task.run_once`
function.  This takes a function and an optional JSON-serializable dictionary of user data,
and submits it to the worker channel once, immediately, bypassing the ``schedule``
parameter of the task object, and deleting the task object immediately afterwards.
This can be quite handy for odd jobs.

..  code-block:: python

    from sisy.models import Task
    from myapp.utils import one_time_only_function

    Task.run_once(one_time_only_function)

For even lazier developers, you don't even have to import the function; just use
the dotted path.

..  code-block:: python

    from sisy.models import Task
    Task.run_once('myapp.utils.one_time_only_function')


Scheduling a one-shot run for some future time
++++++++++++++++++++++++++++++++++++++++++++++

Because a task will not be considered runnable until its ``start_running`` date
has passed, a one-shot run can be scheduled for a future time by providing a
future datetime object to the optional ``delay_until`` parameter on the
:py:meth:`Task.run_once()` class method:

.. code-block:: python

    from sisy.models import Task
    from django.utils.timezone import now
    from datetime import timedelta

    def do_this_later(message):
        print("Finally!")

    three_days_from_now = now() + timedelta(days=3)
    Task.run_once(do_this_later, delay_until=three_days_from_now)

The ``delay_until`` parameter is also available on the :py:meth:`Task.run_iterations`
method, since the :py:meth:`Task.run_once` method is just a shortcut to that method.

.. warning::

    Please note that the ``delay_until`` parameter *must* be an "aware" datetime; that is,
    it must include timezone information.  ``django.utils.timezone.now`` is a good source
    of such a datetime (as in the above sample code), or one may be constructed by providing
    a timezone (such as one obtained from ``django.utils.timezone.get_current_timezone()``) in the
    ``tz`` parameter to the constructor of ``datetime.datetime``.  See snippet below for an example.

.. code-block:: python

    from datetime import datetime, timedelta
    from django.conf import settings
    from django.utils import timezone
    from sisy.models import Task

    OUR_TIMEZONE = timezone.get_current_timezone()

    def do_this_later(message):
        print("This should happen much later...")

    later = datetime.now(tz=OUR_TIMEZONE) + timedelta(days=3)

    Task.run_once(do_this_later, delay_until=later)




