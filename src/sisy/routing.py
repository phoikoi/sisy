from channels.routing import route, include
from sisy.consumers import run_heartbeat, run_task, remove_task
from sisy import RUN_TASK_CHANNEL, KILL_TASK_CHANNEL, HEARTBEAT_CHANNEL

channel_routing = [
    route(HEARTBEAT_CHANNEL, run_heartbeat),
    route(RUN_TASK_CHANNEL, run_task),
    route(KILL_TASK_CHANNEL, remove_task)
]
