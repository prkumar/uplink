Advanced Usage
**************

.. _sync_vs_async:

Swapping Out the Default HTTP Client
====================================

By default, Uplink uses the Requests library as the backing HTTP client.
You can configure this using the :obj:`client` parameter of the
:py:class:`~uplink Consumer` constructor:

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


Synchronous vs. Asynchronous Requests
=====================================

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

Deserializing the Response Body
===============================

Uplink makes it easy to convert an HTTP response body into a custom
Python object, whether you leverage Uplink's built-in support for
libraries such as :py:mod:`marshmallow` or use :py:class:`uplink.loads`
to write custom conversion logic that fits your unique needs.

At the least, you need to specify the expected return type using a
decorator from the :py:class:`uplink.returns` module. For example,
:py:class:`uplink.returns.from_json` is handy when working with APIs that
provide JSON responses:

.. code-block:: python

    @returns.from_json(User)
    @get("users/{username}")
    def get_user(self, username): pass

Python 3 users can alternatively use a return type hint:

.. code-block:: python

    @returns.from_json
    @get("users/{username}")
    def get_user(self, username) -> User: pass

Next, if your objects (e.g., :py:obj:`User`) are not defined
using a library for whom Uplink has built-in support (such as
:py:mod:`marshmallow`), you will also need to register a strategy that
tells Uplink how to convert the HTTP response into your expected return
type.

To this end, the :py:class:`uplink.loads` class has various methods for
defining deserialization strategies for different formats. For the above
example, we can use :py:meth:`uplink.loads.from_json`:

.. code-block:: python

    @loads.from_json(User)
    def user_loader(user_cls, json):
        return user_cls(json["id"], json["username"])

The decorated function, :py:func:`user_loader`, can then be passed into the
:py:attr:`converter` constructor parameter when instantiating a
:py:class:`uplink.Consumer` subclass:

.. code-block:: python

    my_client = MyConsumer(base_url=..., converter=user_loader)

Alternatively, you can add the :py:meth:`uplink.loads.install` decorator to
register the converter function as a default converter, meaning the converter
will be included automatically with any consumer instance and doesn't need to
be explicitly provided through the :py:obj:`converter` parameter:

.. code-block:: python
   :emphasize-lines: 1

    @loads.install
    @loads.from_json(User)
    def user_loader(user_cls, json):
        return user_cls(json["id"], json["username"])

.. note::

    For API endpoints that return collections (such as a list of
    :py:obj:`User`), Uplink offers built-in support for :ref:`converting
    lists and mappings`: simply define a deserialization strategy for
    the element type (e.g., :py:obj:`User`), and Uplink handles the
    rest!

.. _`custom response handler`:

Custom Response and Error Handling
==================================

.. versionadded:: 0.4.0

To register a custom response or error handler, decorate a function with
the :py:class:`response_handler` or :py:class:`error_handler` decorator.

.. note::

    Unlike consumer methods, these functions should be defined outside
    of a class scope.

For instance, the function :py:func:`returns_success` defined below is a
response handler that outputs whether or not the request was successful:

.. code-block:: python

    @uplink.response_handler
    def returns_success(response):
        return response.status == 200

Now, :py:func:`returns_success` can be used as a decorator to inject its custom
response handling into any request method:

.. code-block:: python

    @returns_success
    @put("/todos")
    def create_todo(self, title):
        """Creates a todo with the given title."""

To apply the function's handling onto all request methods of a
:py:class:`~uplink.Consumer` subclass, we can simply use the registered
handler as a class decorator:

.. code-block:: python

    @returns_success
    class TodoApp(uplink.Consumer):
        ...

Similarly, functions decorated with :py:class:`error_handler` are registered
error handlers. When applied to a request method, these handlers are
invoked when the underlying HTTP client fails to execute a request:

.. code-block:: python

    @error_handler
    def raise_api_error(exc_type, exc_val, exc_tb):
        # wrap client error with custom API error
        ...

Notably, handlers can be stacked on top of one another to chain their
behavior:

.. code-block:: python

    @raise_api_error
    @returns_success
    class TodoApp(uplink.Consumer):
        ...

.. _`annotating constructor arguments`:

Annotating :py:meth:`__init__` Arguments
========================================

.. versionadded:: 0.4.0

Function annotations like :py:class:`Query` and :py:class:`Header` can
be used with constructor arguments of a :py:class:`~uplink.Consumer` subclass.
When a new consumer instance is created, the value of these arguments are
applied to all requests made through that instance.

For example, the following consumer accepts the API access token as the
constructor argument :py:attr:`access_token`:

.. code-block:: python

    class GitHub(uplink.Consumer):

        def __init__(self, access_token: uplink.Query):
            ...

        @uplink.post("/user")
        def update_user(self, **info: Body):
            """Update the authenticated user"""

Now, all requests made from an instance of this consumer class will be
authenticated with the access token passed in at initialization:

.. code-block:: python

    github = GitHub("my-github-access-token")

    # This request will include the `access_token` query parameter set from
    # the constructor argument.
    github.update_user(bio="Beam me up, Scotty!")


.. _`session property`:

Persistence Across Requests from a :obj:`Consumer`
==================================================

.. versionadded:: 0.6.0

The :py:obj:`session` property of a :class:`~uplink.Consumer` instance exposes
the instance's configuration and allows for the persistence of certain
properties across requests sent from that instance.

As an alternative to :ref:`annotating constructor arguments`, you can
provide default headers and query parameters for requests sent from a
consumer instance through its :py:obj:`session` property:

.. code-block:: python

    class TodoApp(uplink.Consumer):

        def __init__(self, username, password)
            # Creates the API token for this user
            api_key = create_api_key(username, password)

            # Send the API token as a query parameter with each request.
            self.session.params["api_key"] = api_key

        # Both 'api_key' and 'sort_by' are sent.
        def get_todos(self, sort_by: uplink.Query("sort_by")):
            """Retrieves all todo items."""

Similar to the annotation style, headers and query parameters added
through the :obj:`session` are applied to all requests sent from the
consumer instance.

Notably, in case of conflicts, the method-level headers and parameters
override the session-level, but the method-level properties are not
persisted across requests.
