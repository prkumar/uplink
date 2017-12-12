Installation
============

Using pip
---------

With :program:`pip` (or :program:`pipenv`), you can install Uplink simply by
typing:

::

    $ pip install uplink


Download the Source Code
------------------------

Uplink's source code is in a `public repository hosted on GitHub
<https://github.com/prkumar/uplink>`__.

As an alternative to installing with :program:`pip`, you could clone the
repository,

::

    $ git clone https://github.com/prkumar/uplink.git

then, install; e.g., with :file:`setup.py`:

::

    $ cd uplink
    $ python setup.py install

Extras
------

These are optional integrations and features that extend the library's core
functionality. When installing Uplink with ``pip``, you can specify any of
the following extras:

===============  =============================================================
Extra Name       Description
===============  =============================================================
``aiohttp``      Enables :py:class:`uplink.AiohttpClient`,
                 for sending non-blocking requests and receiving awaitable
                 responses.
``marshmallow``  Enables :py:class:`uplink.MarshmallowConverter`,
                 for converting JSON responses directly into Python objects
                 using :py:class:`marshmallow.Schema`.
``twisted``      Enables :py:class:`uplink.TwistedClient`,
                 for sending non-blocking requests and receiving
                 :py:class:`~twisted.internet.defer.Deferred` responses.
===============  =============================================================

To download all available features, run

::

    $ pip install uplink[aiohttp, marshmallow, twisted]