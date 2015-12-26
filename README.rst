dynipify
========

Update DYNHOST record on OVH DNS Servers with IP obtains from ipify
infrastructure.

Installation
------------

First, get sources from github:

.. code:: bash

    # git clone https://github.com/bougie/dynipify.git

It is recommended to run dynipify in a separate virtualenv.
Create a virtual environment :

.. code:: bash

    # virtualenv --python=/path/to/python3 ~/.python/dynipify

Then, activate it and install all dependancies of dynipify:

.. code:: bash

    # . ~/.python/dynipify/bin/activate
    (dynipify)# pip install -r requirements.txt

You have now a running environment ! Check it with showing help message
of the command:

.. code:: bash

    (dynipify)# python dynipify.py --help

No error should appear.

Configuration
-------------

1. OVH Credentials
******************

Copy ``ovh.conf.example`` to ``ovh.conf`` in three of the next locations:
- Current working directory: ``./ovh.conf``
- Current user's home directory: ``~/.ovh.conf``
- System wide configuration: ``/etc/ovh.conf``

2. Dynipify Settings
********************

Copy ``config.py.sample`` to ``config.py`` in the dynipify source directory

3. Appplication key
*******************

Before launching an update command, you have to authorize the dynipify
application to use your API account
`go to the OVH page <https://api.ovh.com/createApp/>`_.

4. Consummer key
****************

Request a consummer_key by using embded command in dynipify:

.. code:: bash

    (dynipify)# python dynipify.py auth

And follow steps on the screen.

Usage
-----

Simply launch the next command to update all your records specified in config.py:

.. code:: bash

    (dynipify)# python dynipify.py update
