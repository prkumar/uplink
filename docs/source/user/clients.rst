Clients
*******

To use a common English metaphor: Uplink stands on the shoulders of giants.

Uplink doesn't implement any code to handle HTTP protocol stuff
directly; for that, the library delegates to an actual HTTP client, such
as Requests or Aiohttp. Whatever backing client you choose, when a
request method on a :class:`~uplink.Consumer` subclass is invoked, Uplink
ultimately interacts with the backing library's interface, at minimum to
submit requests and read responses.

This section covers the interaction between Uplink and the backing HTTP
client library of your choosing, including how to specify your
selection.

.. _swap_default_http_client:

Swapping Out the Default HTTP Session
=====================================

By default, Uplink sends requests using the Requests library. You can
configure the backing HTTP client object using the :obj:`client`
parameter of the :py:class:`~uplink.Consumer` constructor:

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

Further, this also applies for session objects from other HTTP client
libraries that Uplink supports, such as :mod:`aiohttp` (i.e., a custom
:class:`~aiohttp.ClientSession` works here, as well).

Following the above example, the :obj:`client` parameter also accepts an
instance of any :class:`requests.Session` subclass. This makes it easy
to leverage functionality from third-party Requests extensions, such as
`requests-oauthlib`_, with minimal integration overhead:

.. code-block:: python

    from requests_oauthlib import OAuth2Session

    session = OAuth2Session(...)
    api = MyApi(BASE_URL, client=session)


.. |requests-oauthlib| replace:: ``requests-oauthlib``
.. _`requests-oauthlib`: https://github.com/requests/requests-oauthlib

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
