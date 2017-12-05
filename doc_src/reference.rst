API reference
=============

..  py:module:: sisy.models

..  py:function:: task_with_callable(the_callable, label=None, schedule=sisy.DEFAULT_SCHEDULE, userdata=None, pk_override=None)

    :param the_callable: The function to call; can be object or string with dotted path.
    :type the_callable: object or str
    :param str label: The string label for the task object.  If not specified, will be set to the dotted path of the callable.
    :param str schedule: The *cron*-formatted string specifying the execution schedule for the task.  If not specified, will be set to the default schedule as defined in the Django setting ``SISY_DEFAULT_SCHEDULE``, or, if that is not set, to '\* \* \* \* \*', which will execute once per minute.
    :param dict userdata: A Python dictionary of JSON-serializable data.  If not specified, the dictionary will be empty.
    :param int pk_override: For use only when creating tasks by dotted path to Django model instance methods; provides instance primary key to enable retrieval of the model object in the remote worker.
    :return: the Task object for the specified function.  Must be saved before it will become active.
    :rtype: :py:class:`sisy.models.Task`

..  py:class:: Task

    **Public fields**

    These fields are safe to modify directly in the task object, though it is
    usually easier to use the class methods to set them on task creation.

    :ivar str label: Name of the task, by default the same as the dotted Python path to the callable function
    :ivar str schedule: Cron-format schedule for running the task
    :ivar bool enabled: The task will not be scheduled if this field is false
    :ivar datetime start_running: Datetime when the task is first eligible to run
    :ivar datetime end_running: Datetime when the task is no longer eligible to run
    :ivar bool wait_for_schedule: Should the task wait for its first scheduled run, or run immediately
    :ivar int iterations: Number of iterations to schedule the task (0 means infinite)
    :ivar bool allow_overlap: If false, sisy will not start a second worker on this task while one is already running

    **Internal fields**

    These fields are managed by code in the class methods; it is best to not
    modify them directly.

    :ivar datetime created_at: Datetime when the task was created
    :ivar datetime modified_at: Datetime of the last modification of the task
    :ivar datetime last_run: Datetime of latest task run (default is ``sisy.models.HAS_NOT_RUN``)
    :ivar datetime next_run: Calculated datetime of next scheduled task run
    :ivar str _func_info: Internal dictionary of details about the callable function, stored as JSON
    :ivar str _extra_data: Internal dictionary of userdata, stored as JSON.  Access through the ``userdata`` property.
    :ivar bool running: Internal flag to keep track of whether a worker is currently running this task, to avoid overlap if that has been specified

    .. py:classmethod:: run_iterations(cls, the_callable, iterations=1, label=None, schedule='* * * * * *', userdata=dict, run_immediately=False, delay_until=None)

    :param the_callable: The function to call; can be object or string with dotted path.
    :type the_callable: object or str
    :param int iterations: The number of iterations that this task should run (according to its *cron* schedule)
    :param str label: The string label for the task object.  If not specified, will be set to the dotted path of the callable.
    :param str schedule: The *cron*-formatted string specifying the execution schedule for the task.  If not specified, will be set to '\* \* \* \* \* \*', which will execute the iterations as fast as the ``SISY_HEARTBEAT_FREQUENCY`` setting allows (by default, once per minute).
    :param dict userdata: A Python dictionary of JSON-serializable data.  If not specified, the dictionary will be empty.
    :param bool run_immediately: An optional flag which, if set to True, will cause the first iteration of the task to run immediately, instead of waiting for the *cron* schedule to indicate execution time.
    :param datetime delay_until: If specified, the task will be delayed until the specified datetime by setting the Task object's ``start_running`` field.

    .. py:classmethod:: run_once(cls, the_callable, userdata=dict, delay_until=None)

    :param the_callable: The function to call; can be object or string with dotted path.
    :type the_callable: object or str
    :param dict userdata: A Python dictionary of JSON-serializable data.  If not specified, the dictionary will be empty.
    :param datetime delay_until: If specified, the task will be delayed until the specified datetime by setting the Task object's ``start_running`` field.
