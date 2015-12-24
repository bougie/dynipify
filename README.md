dynipify
========

Update DYNHOST record on OVH DNS Servers with IP obtains from ipify
infrastructure.

INSTALL
-------

Install requirements with pip in a python 3 virtualenv:

    (dynipify)# pip install -r requirements.txt

CONFIG
------

First
- copy `ovh.conf.example` to `ovh.conf` in your home directory
- copy `config.py.sample` to `config.py`
Next, fill them with correct values.

USAGE
-----

You have to manually get a consumer_key and specified it in the ovh.conf file.
