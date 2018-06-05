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

:py:class:`~uplink.Query` parameters can also be added dynamically
by method arguments.

.. code:: python

    @get("group/{id}/users")
    def group_list(self, group_id: Path("id"), sort: Query): pass

For complex query parameter combinations, a :py:class:`~uplink.QueryMap`
can be used:

.. code:: python

    @get("group/{id}/users")
    def group_list(self, group_id: Path("id"), **options: QueryMap): pass

You can set static query parameters for a method using the
:py:class:`~uplink.params` decorator.

.. code:: python

    @params({"client_id": "my-client", "client_secret": "****"})
    @get("users/{username}")
    def get_user(self, username): pass


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

Deserializing the Response Body
===============================

Uplink makes it easy and optional to convert HTTP response bodies into
data model objects, whether you leverage Uplink's built-in support for
libraries such as :py:mod:`marshmallow` (see
:py:class:`uplink.converters.MarshmallowConverter`) or use
:py:class:`uplink.loads` to write custom conversion logic that fits your
unique needs.

At the least, you need to specify the expected return type using a
decorator from the :py:class:`uplink.returns` module.
:py:class:`uplink.returns.json` is handy when working with APIs that
provide JSON responses:

.. code-block:: python

    @returns.json(User)
    @get("users/{username}")
    def get_user(self, username): pass

Python 3 users can alternatively use a return type hint:

.. code-block:: python

    @returns.json
    @get("users/{username}")
    def get_user(self, username) -> User: pass

The final step is to register a strategy that converts the HTTP response
into the expected return type. To this end, :py:meth:`uplink.loads` can
register a function that handles such deserialization for a particular
class and all its subclasses.

.. code-block:: python

    # The base class for all model types, including User from above.
    from models import ModelBase

    # Tell Uplink how to deserialize JSON responses into our model classes:
    @loads.install  # Make this available to all consumer instances.
    @loads.from_json(ModelBase)
    def load_model_from_json(model_cls, json_obj):
        return model_cls.from_json(json_obj)

This step is not required if you define your data model objects using a library
for whom Uplink has built-in support, such as :py:mod:`marshmallow` (see
:py:class:`uplink.converters.MarshmallowConverter`).

.. note::

    For API endpoints that return collections (such as a list of users),
    Uplink just needs to know how to deserialize the element type (e.g.,
    a user), offering built-in support for :ref:`converting lists and
    mappings`.

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
response handler that output whether or not the request was successful:

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

    github = TodoApp("my-github-access-token")

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
