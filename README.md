Python startup files
====================

These are the startup files that I use for the interactive Python shell.

Credits
-------

This is entirely not my work (except a few fixes), all credits to the authors
as noted in the different files.

* jezdez/python-startup

Installation
------------

Get code from Github::

    homesick clone kevinkirkup/spicy-python


### Python Repl Setup

Put this in your shell profile::

    export PYTHONSTARTUP=$HOME/.python/startup.py

In case you haven't saved these files in $HOME/.python make sure to set
PYTHONUSERDIR approppriately, too::

    export PYTHONUSERDIR=/path/to/dir

### IPython Repl Setup

