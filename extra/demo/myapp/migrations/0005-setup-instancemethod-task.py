# -*- coding: utf-8 -*-
from django.db import migrations
from sisy.models import task_with_callable, taskinfo_with_label

TASK_NAME = 'myapp.models.ModelFoo.InstanceMethod'
TASK_LABEL = 'MIGRATION-myapp-0005-setup-instancemethod-task'

def add_repeating(apps, schema_editor):
    ModelFoo = apps.get_model('myapp.ModelFoo')
    newFoo = ModelFoo(name='Test Foo')
    newFoo.save()

    task = task_with_callable(
        TASK_NAME,
        label=TASK_LABEL,
        schedule='* * * * *',
        pk_override=newFoo.pk,
    )
    task.save()

def remove_repeating(apps, schema_editor):
    Task = apps.get_model('sisy.Task')
    ModelFoo = apps.get_model('myapp.ModelFoo')

    task = Task.objects.get(label=TASK_LABEL)
    task.enabled=False
    task.save()

    oldFooPK = taskinfo_with_label(TASK_LABEL)['model_pk']
    oldFoo = ModelFoo.objects.get(pk=oldFooPK)
    oldFoo.delete()

    task.delete()
    
class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0004-setup-staticmethod-task'),
        ('sisy', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(add_repeating, reverse_code=remove_repeating)
    ]
