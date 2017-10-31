Advanced Usage
**************


.. _`non-blocking requests`:


Swapping out the Requests Library
=================================

By default, Uplink uses the Requests library. But, you can override the
underlying HTTP client that a consumer uses by setting the constructor
parameter :py:attr:`client`:

.. code-block:: python

    github = GitHub(base_url="...", client=...)


Making Non-Blocking Requests
============================

Notably, the Requests library blocks while it waits for a response. For
non-blocking IO, Uplink comes with support for asyncio and Twisted. For
the former, we use `aiohttp
<http://aiohttp.readthedocs.io/en/stable/>`_. The Twisted client is
inspired by `requests-threads
<https://github.com/requests/requests-threads>`_.

Adapters for these clients are made available through the subpackage
:py:mod:`uplink.clients`:

.. code-block:: python

    # Create a consumer that returns Twisted Deferred responses.
    # This should work with all supported Python versions.
    github = GitHub(base_url="...", client=uplink.clients.Twisted)

    # Create a consumer that returns awaitable responses.
    # This should work with Python 3.4 and above.
    github = GitHub(base_url="...", client=uplink.clients.Aiohttp)

