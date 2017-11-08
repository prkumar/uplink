Advanced Usage
**************

Swapping out the Requests Library
=================================

By default, Uplink uses the Requests library. But, you can override the
underlying HTTP client that a consumer uses by setting the constructor
parameter :py:attr:`client`:

.. code-block:: python

    github = GitHub(base_url="...", client=...)

.. _`non-blocking requests`:

Making Non-Blocking Requests
============================

Notably, the default Requests library blocks while it waits for a response. For
non-blocking IO, Uplink comes with support for asyncio and Twisted.

For short examples with each asynchronous client, checkout
`this Gist <https://gist.github.com/prkumar/4e905edb988bc3d3d95e680ef043f934>`_.

Asyncio
-------

For asyncio support, Uplink offers a `aiohttp
<http://aiohttp.readthedocs.io/en/stable/>`_ client adapter,
:py:class:`uplink.AiohttpClient`:

.. code-block:: python

    # Create a consumer that returns awaitable responses.
    # This should work with Python 3.4 and above.
    github = GitHub(base_url="...", client=uplink.AiohttpClient())

Twisted
-------

To have your consumer return `Twisted Deferred
<https://twistedmatrix.com/documents/current/core/howto/defer.html>`_
responses, use a :py:class:`uplink.TwistedClient`:

.. code-block:: python

    # Create a consumer that returns Twisted Deferred responses.
    # This should work with all supported Python versions.
    github = GitHub(base_url="...", client=uplink.TwistedClient())

This client is inspired by `requests-threads
<https://github.com/requests/requests-threads>`_.
