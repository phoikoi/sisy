def daily_maintenance(message):
    task = message['task']
    print(f"Running daily maintenance function from task #{task.id} ({task.label})")
    print(f"This function's module path is {task.funcinfo['func_path']}")