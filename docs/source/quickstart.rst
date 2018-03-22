Quickstart
**********

Decorators and function annotations indicate how a request will be handled.

Request Method
==============

Uplink offers decorators that turn any method into a request definition. These
decorators provide the request method and relative URL of the intended
request: :py:obj:`~uplink.get`, :py:obj:`~uplink.post`,
:py:obj:`~uplink.put`, :py:obj:`~uplink.patch` and :py:obj:`~uplink.delete`.

The relative URL of the resource is specified in the decorator.

.. code:: python

    @get("users/list")

You can also specify query parameters in the URL.

.. code:: python

    @get("users/list?sort=desc")

Moreover, request methods must be bound to a :py:class:`~uplink.Consumer`
subclass.

.. code:: python

    class MyApi(Consumer):
        @get("users/list")
        def list_users(self):
            """List all users."""

URL Manipulation
================

A request URL can be updated dynamically using `URI template parameters
<https://tools.ietf.org/html/rfc6570>`__. A simple URI parameter is an
alphanumeric string surrounded by ``{`` and ``}``.

To match the parameter with a method argument, either match the argument's
name with the alphanumeric string, like so

.. code:: python

    @get("group/{id}/users")
    def group_list(self, id): pass

or use the :py:class:`~uplink.Path` annotation.

.. code:: python

    @get("group/{id}/users")
    def group_list(self, group_id: Path("id")): pass

:py:class:`~uplink.Query` parameters can also be added.

.. code:: python

    @get("group/{id}/users")
    def group_list(self, group_id: Path("id"), sort: Query): pass

For complex query parameter combinations, a mapping can be used:

.. code:: python

    @get("group/{id}/users")
    def group_list(self, group_id: Path("id"), options: QueryMap): pass


Request Body
============

An argument's value can be specified for use as an HTTP request body with the
:py:class:`~uplink.Body` annotation:

.. code:: python

    @post("users/new")
    def create_user(self, user: Body): pass

This annotation works well with the **keyword arguments** parameter (denoted
by the `**` prefix):

.. code:: python

    @post("users/new")
    def create_user(self, **user_info: Body): pass

Form Encoded, Multipart, and JSON
=================================

Methods can also be declared to send form-encoded, multipart, and JSON data.

Form-encoded data is sent when :py:class:`~uplink.form_url_encoded` decorates
the method. Each key-value pair is annotated with a :py:class:`~uplink.Field`
annotation:

.. code:: python

    @form_url_encoded
    @post("user/edit")
    def update_user(self, first_name: Field, last_name: Field): pass

Multipart requests are used when :py:class:`~uplink.multipart` decorates the
method. Parts are declared using the :py:class:`~uplink.Part` annotation:

.. code:: python

    @multipart
    @put("user/photo")
    def update_user(self, photo: Part, description: Part): pass

JSON data is sent when :py:class:`~uplink.json` decorates the method. The
:py:class:`~uplink.Body` annotation declares the JSON payload:

.. code:: python

    @uplink.json
    @uplink.patch("/user")
    def update_user(self, **user_info: uplink.Body):
        """Update an authenticated user."""

Header Manipulation
===================

You can set static headers for a method using the :py:class:`~uplink.headers`
decorator.

.. code:: python

    @headers({
        "Accept": "application/vnd.github.v3.full+json",
        "User-Agent": "Uplink-Sample-App"
    })
    @get("users/{username}")
    def get_user(self, username): pass

:py:class:`~uplink.headers` can be used as a class decorator for headers that
need to be added to every request:

.. code:: python

    @headers({
        "Accept": "application/vnd.github.v3.full+json",
        "User-Agent": "Uplink-Sample-App"
    })
    class GitHub(Consumer):
        ...

A request header can be updated dynamically using the :py:class:`~uplink.Header`
function parameter annotation:

.. code:: python

    @get("user")
    def get_user(self, authorization: Header):
        """Get an authenticated user."""


Synchronous vs. Asynchronous
============================

By default, Uplink uses the Requests library to make requests. However, the
``client`` parameter of the :py:class:`~uplink.Consumer` constructor offers a
way to swap out Requests with another HTTP client:

.. code-block:: python

    github = GitHub(BASE_URL, client=...)

Notably, Requests blocks while waiting for a response from a server.
For non-blocking requests, Uplink comes with optional support for
:py:mod:`asyncio` and :py:mod:`twisted`. Checkout `this
example on GitHub <https://github.com/prkumar/uplink/tree/master/examples/async-requests>`_
for more.

Deserializing the Response
==========================

The ``converter`` parameter of the :py:class:`~uplink.Consumer` constructor
accepts an adapter class that handles deserialization of HTTP response objects.

.. code-block:: python

    github = GitHub(BASE_URL, converter=...)

For instance, the :py:class:`~uplink.MarshmallowConverter` adapter turns JSON
HTTP responses into Python objects using the :py:class:`marshmallow.Schema`
object. Checkout `this example on GitHub
<https://github.com/prkumar/uplink/tree/master/examples/marshmallow>`_ for more.

.. _`custom response handler`:

Custom Response and Error Handling
==================================

.. versionadded:: 0.4.0

To register a custom response or error handler, decorate a function with
the :py:class:`response_handler` or :py:class:`error_handler` decorator.

For instance, the function :py:func:`accept_json` defined below is a response
handler that outputs the JSON body of a given response:

.. code-block:: python

    @uplink.response_handler
    def accept_json(response):
        return response.json()

Now, :py:func:`accept_json` can be used as a decorator to inject its custom
response handling into any request method:

.. code-block:: python

    @accept_json
    @get("/todo/{id}")
    def get_todo(self, id):
        """Get the todo with the given id."""

To apply the function's handling onto all request methods of a
:py:class:`~uplink.Consumer` subclass, we can simply use the registered handler
as a class decorator:

.. code-block:: python

    @accept_json
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
    @accept_json
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

    github = TodoApp("my-github-access-token")

    # This request will include the above access token as a query parameter.
    github.update_user(bio="Beam me up, Scotty!")

:py:meth:`_inject` Request Properties
=====================================

.. versionadded:: 0.4.0

As an alternative to :ref:`annotating constructor arguments`, you can achieve
a similar behavior with more control by using the
:py:meth:`Consumer._inject` method. With this method, you can calculate
request properties within plain old python methods.

.. code-block:: python

    class TodoApp(uplink.Consumer):

        def __init__(self, username, password)
            # Create an access token
            api_key = create_api_key(username, password)

            # Inject it.
            self._inject(uplink.Query("api_key").with_value(api_key))

Similar to the annotation style, request properties added with
:py:meth:`~uplink.Consumer._inject` method are applied to all requests made
through the consumer instance.
