.. _install:

Installation
============

Using pip
---------

With :program:`pip` (or :program:`pipenv`), you can install Uplink simply by
typing:

::

    $ pip install -U uplink


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
functionality and typically require an additional dependency.

When installing Uplink with ``pip``, you can specify any of the following
extras, to add their respective dependencies to your installation:

===============  =============================================================
Extra            Description
===============  =============================================================
``aiohttp``      Enables :py:class:`uplink.AiohttpClient`,
                 for `sending non-blocking requests <https://github.com/prkumar/uplink/tree/master/examples/async-requests>`_
                 and receiving awaitable responses.
``marshmallow``  Enables :py:class:`uplink.MarshmallowConverter`,
                 for `converting JSON responses directly into Python objects
                 <https://github.com/prkumar/uplink/tree/master/examples/marshmallow>`_
                 using :py:class:`marshmallow.Schema`.
``pydantic``     Enables :py:class:`uplink.PydanticConverter`,
                 for converting JSON responses directly into Python objects
                 using :py:class:`pydantic.BaseModel`.
``twisted``      Enables :py:class:`uplink.TwistedClient`,
                 for `sending non-blocking requests <https://github.com/prkumar/uplink/tree/master/examples/async-requests>`_ and receiving
                 :py:class:`~twisted.internet.defer.Deferred` responses.
===============  =============================================================

To download all available features, run

::

    $ pip install -U uplink[aiohttp, marshmallow, pydantic, twisted]

