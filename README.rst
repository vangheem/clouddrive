About
=====

Use Amazon Cloud Drive to sync folders on your computer.

Requires setting up amazon api access.

WARNING: This is a pet project I'm doing just for fun to backup files
on my computer. The docs are not exhaustive and it isn't polished.


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

- supervisor
- cleanup old files
- weekly move old files to different folder
    - eventually clean old
- install package
