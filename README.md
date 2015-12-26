dynipify
========

Update DYNHOST record on OVH DNS Servers with IP obtains from ipify
infrastructure.

Installation
------------

First, get sources from github:

    # git clone https://github.com/bougie/dynipify.git

It is recommended to run dynipify in a separate virtualenv.  
Create a virtual environment :

    # virtualenv --python=/path/to/python3 ~/.python/dynipify

Then, activate it and install all dependancies of dynipify:

    # . ~/.python/dynipify/bin/activate
    (dynipify)# pip install -r requirements.txt

You have now a running environment ! Check it with showing help message
of the command:

    (dynipify)# python dynipify.py --help

No error should appear.

Configuration
-------------

**Credentials**

Copy `ovh.conf.example` to `ovh.conf` in three of the next locations:
- Current working directory: ./ovh.conf
- Current user's home directory ~/.ovh.conf
- System wide configuration /etc/ovh.conf

**dynipify settings**

Copy `config.py.sample` to `config.py` in the dynipify source directory

**appplication and consumer key**

Before launching an update command, you have to authorize the dynipify
application to use your API account
[go to the OVH page](https://api.ovh.com/createApp/).

Next, request a consummer_key by using embded command in dynipify:

    (dynipify)# python dynipify.py auth

And follow steps on the screen.

Usage
-----

Simply launch the next command to update all your records specified in config.py:

    (dynipify)# python dynipify.py update
