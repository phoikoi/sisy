from django.conf import settings

__version__ = "1.0b1"

try:
    DEFAULT_SCHEDULE = settings.SISY_DEFAULT_SCHEDULE
except AttributeError:
    DEFAULT_SCHEDULE = '* * * * *'

try:
    HEARTBEAT_CHANNEL = settings.SISY_HEARTBEAT_CHANNEL
except AttributeError:
    HEARTBEAT_CHANNEL = 'sisy.heartbeat'

try:
    RUN_TASK_CHANNEL = settings.SISY_RUN_TASK_CHANNEL
except AttributeError:
    RUN_TASK_CHANNEL = 'sisy.run_task'

try:
    KILL_TASK_CHANNEL = settings.SISY_KILL_TASK_CHANNEL
except AttributeError:
    KILL_TASK_CHANNEL = 'sisy.kill_task'

try:
    HEARTBEAT_FREQUENCY = settings.SISY_HEARTBEAT_FREQUENCY
except AttributeError:
    HEARTBEAT_FREQUENCY = 60 # once a minute, like cron
