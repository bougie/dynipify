.. dynipify documentation master file, created by
   sphinx-quickstart on Sat Dec 26 21:59:01 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to dynipify's documentation!
====================================

Installation
------------

First, get sources from github:

.. code:: bash

    git clone https://github.com/bougie/dynipify.git

It is recommended to run dynipify in a separate virtualenv.
Create a virtual environment :

.. code:: bash

    virtualenv --python=/path/to/python3 ~/.python/dynipify

Then, activate it and install all dependancies of dynipify:

.. code:: bash

    . ~/.python/dynipify/bin/activate
    pip install -r requirements.txt

You have now a running environment ! Check it with showing help message
of the command:

.. code:: bash

    python dynipify.py --help

No error should appear.

Configuration
-------------

OVH Credentials
***************

Copy ``ovh.conf.example`` to ``ovh.conf`` in three of the next locations:
- Current working directory: ``./ovh.conf``
- Current user's home directory: ``~/.ovh.conf``
- System wide configuration: ``/etc/ovh.conf``

File looks like:

.. code:: ini

    [default]
    ; general configuration: default endpoint
    endpoint=ovh-eu
    
    [ovh-eu]
    ; configuration specific to 'ovh-eu' endpoint
    application_key=my_app_key
    application_secret=my_application_secret
    ;consumer_key=my_consumer_key

Appplication key
****************

Before launching an update command, you have to authorize the dynipify
application to use your API account
`go to the OVH page <https://api.ovh.com/createApp/>`_.

Dynipify Settings
*****************

Copy ``config.py.sample`` to ``config.py`` in the dynipify source directory

Config file looks like:

.. code:: python

    # List of all records to update with the SAME current IP Address
    DYNHOSTS = [
    # {'domain': 'domain.tld', 'subdomain': 'sub'},
    ]
    
    # Log level
    # CRITICAL, ERROR, WARNING, INFO, DEBUG
    LOG_LEVEL = 'INFO'


Consummer key
*************

Request a consummer_key by using embded command in dynipify:

.. code:: bash

    python dynipify.py auth

And follow steps on the screen and fill ``consummer_key`` line in
``ovh.conf`` file.

Usage
-----

All next commands assume that you have a working python environment
(with virtualenv for example):

.. code:: bash

    . ~/.python/dynipify/bin/activate

Update
******

Simply launch the ``update`` command to update all your records specified in config.py:

.. code:: bash

    python dynipify.py update


Auth
****

``auth`` is used when you have to purchase a consummer_key for the script (new or renew it):

.. code:: bash

    python dynipify.py auth

Developer Documentation
=======================

.. toctree::
   :glob:
   :maxdepth: 2

   dynipify/*

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

