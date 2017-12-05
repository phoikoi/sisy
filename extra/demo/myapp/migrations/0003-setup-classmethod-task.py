# -*- coding: utf-8 -*-
from django.db import migrations
from sisy.models import task_with_callable

TASK_NAME = 'myapp.models.ModelFoo.ClassMethod'

# probably less fragile than the dynamic method in migration 0002
TASK_LABEL = 'MIGRATION-myapp-0003-setup-classmethod-task'

def add_repeating(apps, schema_editor):
    task = task_with_callable(
        TASK_NAME,
        label=TASK_LABEL,
        schedule='* * * * *',
    )
    task.save()

def remove_repeating(apps, schema_editor):
    Task = apps.get_model('sisy.Task')
    task = Task.objects.get(label=TASK_LABEL)
    task.delete()
    
class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0002-setup-plainfunction-task'),
        ('sisy', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(add_repeating, reverse_code=remove_repeating)
    ]
