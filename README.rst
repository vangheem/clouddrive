About
=====

Use Amazon Cloud Drive to sync folders on your computer.

Requires setting up amazon api access.

WARNING: This is a pet project I'm doing just for fun to backup files
on my computer. The docs are not exhaustive and it isn't polished.


Requirements
============

Python 3 with virtualenv installed

https://virtualenv.readthedocs.org/en/latest/


Quickstart
==========

Clone it::

    git clone git@github.com:vangheem/clouddrive.git
    cd clouddrive

Get config setup::

    cp config-sample.ini config.ini

and then fill in config values in config.ini


Finish install::

    path/to/python-virtualenv .
    make install
    make run

Then open http://127.0.0.1:5000 in your browser and configure.


TODO
====

- install package
