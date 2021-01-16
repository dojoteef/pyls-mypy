Mypy plugin for PYLS
======================

This is a plugin for the Palantir's Python Language Server (https://github.com/palantir/python-language-server)

It, like mypy, requires Python 3.2 or newer.


Installation
------------

Install into the same virtualenv as pyls itself.

``pip install pyls-mypy``

Configuration
-------------

Depending on your editor, the configuration should be roughly like this:

::

    "pyls":
    {
        "plugins":
        {
            "pyls_mypy":
            {
                "enabled": true,
            }
        }
    }
