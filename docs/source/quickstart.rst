Quickstart
**********

Ready to write your first API client with Uplink? This guide will
walk you through what you'll need to know to get started.

**First**, make sure you've :ref:`installed (or updated) Uplink <install>`!

Consuming Web APIs
==================

Writing a **structured** API client with Uplink is very simple.

The first step is to define a :class:`Consumer` subclass for your API client.
For example, here's the beginning of our GitHub client (we'll add some
methods to this class soon):

.. code:: python

   import uplink

   class GitHub(uplink.Consumer):
      ...

When creating an instance of this client, we can use the :obj:`base_url`
constructor argument to identify the target service. In our case, it's
GitHub's public API:

.. code:: python

   github = GitHub(base_url="https://api.github.com/")

.. note::

    :obj:`base_url` is especially useful to create clients for separate
    instances of an API service; for example, we could use this GitHub
    consumer to also create clients for any GitHub Enterprise instance,
    not just the public https://github.com service. (Another example
    involves creating separate clients for a company's production and
    staging environments, which are typically not accessible from the
    same base URL but expose the same API endpoints.)

So far, this class looks like any other Python subclass. The real magic
happens when you define methods using one of Uplink's HTTP method
decorators, which we cover next.

Making a Request
================

Making a request with Uplink is *literally* as simple as decorating a method.

Any method of a :class:`Consumer` subclass can be
decorated with one of Uplink's HTTP method decorators:
:class:`~uplink.get`, :class:`~uplink.post`, :class:`~uplink.put`,
:class:`~uplink.patch`, and :class:`~uplink.delete`:

.. code::

    class GitHub(Consumer):
        @get("repositories")
        def get_repos(self):
            """List all public repositories."""

The decorator's first argument is the resource endpoint (this
is the relative URL path from :class:`base_url`, which we covered above):

.. code:: python

    @get("/repositories")

You can also specify query parameters:

.. code:: python

    @get("repositories?since=364")

Finally, invoke the method to send a request:

.. code:: python

    >>> github = GitHub(base_url="https://api.github.com/")
    >>> print(github.get_repos())
    <Response [200]>

By default, uplink uses `Requests
<https://github.com/requests/requests>`_, so the response we get back
from GitHub is wrapped in a :class:`requests.Response` instance.
(If you want, you can :ref:`swap out <sync_vs_async>` Requests for a
different backing HTTP client.)


URL Manipulation
================

A method's resource endpoint can be updated dynamically using `URI template
parameters <https://tools.ietf.org/html/rfc6570>`__. A simple URI parameter
is an alphanumeric string surrounded by ``{`` and ``}``.

To match the parameter with a method argument, either match the argument's
name with the alphanumeric string, like so

.. code:: python

    @get("users/{username}")
    def get_user(self, username): pass

or use the :py:class:`~uplink.Path` annotation.

.. code:: python

    @get("users/{username}")
    def get_user(self, username: Path("username")): pass

:py:class:`~uplink.Query` parameters can also be added dynamically
by method arguments.

.. code:: python

    @get("users/{username}/repos")
    def get_repos(self, username, sort: Query): pass

For complex query parameter combinations, a :py:class:`~uplink.QueryMap`
can be used:

.. code:: python

    @get("users/{username}/repos")
    def get_repos(self, username, **options: QueryMap): pass

You can set static query parameters for a method using the
:py:class:`~uplink.params` decorator.

.. code:: python

    @params({"client_id": "my-client", "client_secret": "****"})
    @get("users/{username}")
    def get_user(self, username): pass

:py:class:`~uplink.params` can be used as a class decorator for query
parameters that need to be added to every request:

.. code:: python

    @params({"client_id": "my-client", "client_secret": "****"})
    class GitHub(Consumer):
        ...


Request Body
============

A argument's value can be specified for use as an HTTP request body with the
:py:class:`~uplink.Body` annotation:

.. code:: python

    @post("user/repos")
    def create_repo(self, repo: Body): pass

This annotation works well with the **keyword arguments** parameter (denoted
by the `**` prefix):

.. code:: python

    @post("user/repos")
    def create_repo(self, **repo_info: Body): pass

Form Encoded, Multipart, and JSON
=================================

Methods can also be declared to send form-encoded, multipart, and JSON data.

Form-encoded data is sent when :py:class:`~uplink.form_url_encoded` decorates
the method. Each key-value pair is annotated with a :py:class:`~uplink.Field`
annotation:

.. code:: python

    @form_url_encoded
    @patch("user")
    def update_user(self, name: Field, email: Field): pass

Multipart requests are used when :py:class:`~uplink.multipart` decorates the
method. Parts are declared using the :py:class:`~uplink.Part` annotation:

.. code:: python

    @multipart
    @put("user/photo")
    def upload_photo(self, photo: Part, description: Part): pass

JSON data is sent when :py:class:`~uplink.json` decorates the method. The
:py:class:`~uplink.Body` annotation declares the JSON payload:

.. code:: python

    @uplink.json
    @uplink.patch("user")
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

.. _sync_vs_async:

Synchronous vs. Asynchronous
============================

By default, Uplink uses the Requests library to make requests. However, the
``client`` parameter of the :py:class:`~uplink.Consumer` constructor offers a
way to swap out Requests with another HTTP client:

.. code-block:: python

    github = GitHub(BASE_URL, client=...)

Also, you can use the ``client`` parameter to pass in your own `Requests session
<http://docs.python-requests.org/en/master/user/advanced/#session-objects>`_
object:

.. code-block:: python

    session = requests.Session()
    session.verify = False
    github = GitHub(BASE_URL, client=session)

Notably, Requests blocks while waiting for a response from a server. For
non-blocking requests, Uplink comes with built-in (but opptional)
support for :py:mod:`asyncio` and :py:mod:`twisted`. Checkout `this
example on GitHub
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
