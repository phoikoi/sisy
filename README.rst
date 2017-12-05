
sisy
====

Sisy is a Django package which uses the `Channels <https://channels.readthedocs.io/en/latest/>`_ message-passing infrastructure to run functions
in worker processes.  In other words, it lets you hand off work to background processes in various
ways, rather than having long-running processes stall your web requests.

Sisy has the following requirements and compatibilities:

* Python 3.6 or above
* `Django <https://djangoproject.com/>`_ 1.11 or above, including 2.x
* `Channels <https://channels.readthedocs.io/en/latest/>`_ 1.1.8 or above (earlier versions may work but no guarantees)

Sisy is released under the `MIT License <https://opensource.org/licenses/MIT>`_.

.. _ya-task-runner:

Why yet another task runner package?
------------------------------------

There are already several fine Python packages which function as task runners,
such as `celery <http://www.celeryproject.org/>`_, `rq <http://python-rq.org/>`_,
and others, but I wanted to have a package that worked seamlessly within the
Channels architecture, in order to avoid duplication of effort.

Design goals
------------

Sisy has a few design goals that it is good to keep in mind when evaluating
whether it will fit your particular use case:

*   It is designed to work with tasks that are similar to those one would
    work with using the Unix *cron* utility.  In other words, its tasks
    are expected to run on a frequency scale of minutes, hours, and days rather
    than seconds or milliseconds.

*   It is designed for small to medium installations.  I think it probably could
    handle a surprisingly large site, since it is possible to separate its
    workers, objects, and messages onto their own infrastructure through the
    use of such tools as Django database routing, channel layers, and separate
    redis servers.  But it has not been tested in these scenarios.

*   It is designed with developer ease of use in mind.  It does lack certain facilities
    such as interruptibility, but such features can be designed into the functions
    that handle the task messages, and of course those functions can in turn send
    other messages if necessary.

Quick howto
-----------

You really need to read the `full docs <http://phoikoi.github.io/sisy>`_, but here
is a super-fast crash course.

.. code-block:: python

   from sisy.models import task_with_callable

   task = task_with_callable(
       'mymodule.myfunction', # dotted path to function
       label='weekday-business-hours-function', # any string you want here really
       schedule='0,15,30,45 9-17 * * mon-fri', # Run every 15 minutes 9am-5pm on weekdays
   )
   
   # The task doesn't become active until you save it
   task.save()

There are other goodies in there, such as one-shot task runs, specified number of iterations,
beginning and ending dates, etc.  You can also create tasks in Django data migration files,
which can be really handy for standard tasks you want to always be running. Look at the docs.

       
    Note: There is a demo project in the github repo, under ``extra/demo``. This
    project is very basic, but provides concrete examples of using Sisy in
    various ways, including data migrations. This project also functions
    as the host project for generating the docs.

You can find the full documentation for Sisy at `the Github Pages site for this repo <http://phoikoi.github.io/sisy>`_.

