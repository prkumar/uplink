Clients
*******

.. _swap_default_http_client:

Swapping Out the Default HTTP Client
====================================

By default, Uplink sends requests using the Requests library. You can
configure the backing HTTP client using the :obj:`client` parameter of the
:py:class:`~uplink.Consumer` constructor:

.. code-block:: python

    github = GitHub(BASE_URL, client=...)

For example, you can use the :obj:`client` parameter to pass in your own
`Requests session
<http://docs.python-requests.org/en/master/user/advanced/#session-objects>`_
object:

.. code-block:: python

    session = requests.Session()
    session.verify = False
    github = GitHub(BASE_URL, client=session)

.. _sync_vs_async:

Synchronous vs. Asynchronous
============================

Notably, Requests blocks while waiting for a response from the server. For
non-blocking requests, Uplink comes with built-in (but optional)
support for :mod:`aiohttp` and :mod:`twisted`.

For instance, you can provide the :class:`~uplink.AiohttpClient` when
constructing a :class:`~uplink.Consumer` instance:

.. code:: python

   from uplink import AiohttpClient

   github = GitHub(BASE_URL, client=AiohttpClient())


Checkout `this example on GitHub
<https://github.com/prkumar/uplink/tree/master/examples/async-requests>`_
for more.

