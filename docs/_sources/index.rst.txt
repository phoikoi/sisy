..  sisy documentation master file, created by
    sphinx-quickstart on Mon Nov 13 04:56:16 2017.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

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

.. note::

    There is a demo project in the github repo, under ``extra/demo``. This
    project is very basic, but provides concrete examples of using Sisy in
    various ways, including data migrations. This project also functions
    as the host project for generating these docs.

**Table of Contents**


..  toctree::
    :maxdepth: 2

    installation
    using
    data_migrations
    reference
    release_notes
