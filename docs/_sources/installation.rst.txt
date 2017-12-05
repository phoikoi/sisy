.. _installation:

Installation
============

In order to use Sisy, you must first `install Channels <http://channels.readthedocs.io/en/latest/installation.html>`_. Once you have it up and running,
proceed with the steps below. If you haven't used Channels before, you may want to
look through some of the Channels docs, including `Channels Concepts <http://channels.readthedocs.io/en/latest/concepts.html>`_ and the `Getting Started guide <http://channels.readthedocs.io/en/latest/getting-started.html>`_.

* Install Sisy from PyPI: ``pip install -U sisy``
* Add Sisy to your :setting:`INSTALLED_APPS` list:

    .. code-block:: python
        :emphasize-lines: 8-9

        INSTALLED_APPS = [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'channels',
            'sisy.apps.SisyConfig',
        ]

* Add Sisy's routing to your ``routing.py`` file:

    .. code-block:: python
        :linenos:
        :emphasize-lines: 4

        from channels.routing import route, include

        channel_routing = [
            include('sisy.routing.channel_routing'),
        #    route("websocket.connect", ws_add),
        #    route("websocket.receive", ws_message),
        #    route("websocket.disconnect", ws_disconnect),
        ]

*   Make sure there is at least one worker running which listens to the channels
    that Sisy sends its messages on (see `Project Settings`_ below).

*   Start the ``sisy_heartbeat`` management command to provide the heartbeat messages
    to Sisy.  This can be easily run alongside ``daphne`` as it uses very little in
    terms of CPU load.

*   Now you can :ref:`start using Sisy <using-sisy>`.

Project settings
----------------

All of these settings are optional. If you already have an existing
django/channels project, you probably already have a channel name
scheme.  You can adjust Sisy's names to fit your pattern with these
settings, if necessary.  You can also adjust the frequency of the
"clock tick" messages that Sisy sends to its scheduling code.

:setting:`SISY_HEARTBEAT_CHANNEL` (default: ``sisy.heartbeat``)

    *(string)* Provides the channel name for Sisy to use for the heartbeat messages.

:setting:`SISY_RUN_TASK_CHANNEL` (default: ``sisy.run_task``)

    *(string)* Provides the channel name for Sisy to run the tasks on a worker.

:setting:`SISY_KILL_TASK_CHANNEL` (default: ``sisy.kill_task``)

    *(string)* Provides the channel name for Sisy to run the task reaper (to kill completed tasks.)

:setting:`SISY_HEARTBEAT_FREQUENCY` (default: ``60``)

    *(integer)* Determines the frequency (in seconds) of Sisy's heartbeat messages.  This sets the
    bound on task frequency; no task can execute more frequently than this setting. Consequently, if you need
    more frequent task runs, set this lower (probably not lower than about 5, as Sisy is not designed
    to handle very high frequency tasks) and add the optional sixth field to your frequently-called task's schedule,
    to specify the seconds; e.g. ``* * * * * */30`` will make the task eligible for execution every thirty
    seconds.

:setting:`SISY_DEFAULT_SCHEDULE` (default: ``'* * * * *'``)

    *(string)* Provides the default *cron* schedule for Sisy's tasks.  The default
    causes the task to run once per minute.