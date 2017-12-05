# -*- coding: utf-8 -*-
from pathlib import Path
from django.db import migrations
from sisy.models import task_with_callable
from myapp.utilities import daily_maintenance

# .../sisy/extra/demo/myapp/migrations/0002-setup-plainfunction-task.py
_MIGRATION_PATH = Path(__file__)

# 0002-setup-plainfunction
_TASK_LABEL_STEM = _MIGRATION_PATH.stem

# myapp
_TASK_LABEL_APP = _MIGRATION_PATH.parent.parent.name

# MIGRATION-myapp-0002-setup-plainfunction
TASK_LABEL = f"MIGRATION-{_TASK_LABEL_APP}-{_TASK_LABEL_STEM}"

def add_repeating(apps, schema_editor):
    task = task_with_callable(
        daily_maintenance,
        label=TASK_LABEL,
        schedule='30 0 * * * */15',
    )
    task.save()

def remove_repeating(apps, schema_editor):
    Task = apps.get_model('sisy.Task')
    task = Task.objects.get(label=TASK_LABEL)
    task.delete()
    
class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0001_initial'),
        ('sisy', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(add_repeating, reverse_code=remove_repeating)
    ]
