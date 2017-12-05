Release notes
=============

1.0b1 (2017-12-04)
------------------

First release in public repo, history from private repo scrubbed.

**Notes:**

*  Needs more tests
*  Task execution of instance methods only allows for integer primary keys, need to
   find solution for e.g. UUIDs and strings.

1.0b2 (2017-12-05)
------------------

*  Fixed missing management command (somewhat inconvenient, as this is what runs the main
   heartbeat command...)

1.0b3 (2017-12-05)
------------------

*  Fixed missing arrow dependency in setup.py (such are the tribulations of a new pypi package)

