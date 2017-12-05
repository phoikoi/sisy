"""
django-channels consumers for sisy
"""
import arrow
import pytz
from django.conf import settings
from django.utils import timezone

from sisy.models import Task

try:
    TICK_FREQ = settings.SISY_TICK_FREQUENCY
except AttributeError:
    TICK_FREQ = 60 # seconds

TIME_FORMAT = "%Y-%m-%d %H:%M:%S %Z"
TZ = pytz.timezone(settings.TIME_ZONE)

def run_heartbeat(message):
    """Internal ``CLOCK_CHANNEL`` consumer to process task runs"""
    then = arrow.get(message['time'])
    now = arrow.get()

    if (now - then) > timezone.timedelta(seconds=(TICK_FREQ+1)):
        pass # discard old ticks
    else:
        Task.run_tasks()

def run_task(message):
    """Internal ``RUN_TASK`` consumer to run the task's callable"""
    task = Task.objects.get(pk=message['id'])
    if task.allow_overlap:
        task.run(message)
    else:
        if not task.running:
            task.running = True
            task.save()
            try:
                task.run(message)
            finally:
                task.running = False
                task.save()

def remove_task(message):
    """Internal ``KILL_TASK`` consumer to remove retired tasks"""
    task = Task.objects.get(pk=message['id'])
    task.delete()
