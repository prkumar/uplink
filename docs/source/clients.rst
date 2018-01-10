HTTP Clients
************

The ``client`` parameter of the :py:class:`Consumer` constructor offers a way
to swap out Requests with another HTTP client, including those listed here:

.. code-block:: python

    github = GitHub(BASE_URL, client=...)


Requests
========

.. autoclass:: uplink.RequestsClient

Aiohttp
=======

.. autoclass:: uplink.AiohttpClient

Twisted
=======

.. autoclass:: uplink.TwistedClient