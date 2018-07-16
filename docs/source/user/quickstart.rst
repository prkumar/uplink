.. _quickstart:

Quickstart
**********

Ready to write your first API client with Uplink? This guide will
walk you through what you'll need to know to get started.

**First**, make sure you've :ref:`installed (or updated) Uplink <install>`!

Defining an API Client
======================

Writing a **structured** API client with Uplink is very simple.

The first step is to define a :class:`Consumer` subclass for your API client.
For example, here's the beginning of our GitHub client (we'll add some
methods to this class soon):

.. code:: python

   from uplink import Consumer

   class GitHub(Consumer):
      ...

When creating an instance of this client, we can use the :obj:`base_url`
constructor argument to identify the target service. In our case, it's
GitHub's public API:

.. code:: python

   github = GitHub(base_url="https://api.github.com/")

.. note::

    :obj:`base_url` is especially useful for creating clients that
    target separate services with similar APIs; for example, we could use
    this GitHub consumer to also create clients for any GitHub
    Enterprise instance, for projects hosted outside of the public
    `GitHub.com <https://github.com>`_ service. (Another example is
    creating separate clients for a company's production and staging
    environments, which are typically hosted on separate domains but
    expose the same API endpoints.)

So far, this class looks like any other Python subclass. The real magic
happens when you define methods using one of Uplink's HTTP method
decorators, which we cover next.

Making a Request
================

Making a request with Uplink is *literally* as simple as decorating a method.

Any method of a :class:`Consumer` subclass can be
decorated with one of Uplink's HTTP method decorators:
:class:`~uplink.get`, :class:`~uplink.post`, :class:`~uplink.put`,
:class:`~uplink.patch`, :class:`~uplink.head`, and :class:`~uplink.delete`:

.. code::

    class GitHub(Consumer):
        @get("repositories")
        def get_repos(self):
            """List all public repositories."""

The decorator's first argument is the resource endpoint (this
is the relative URL path from :class:`base_url`, which we covered above):

.. code:: python

    @get("repositories")

You can also specify query parameters:

.. code:: python

    @get("repositories?since=364")

Finally, invoke the method to send a request:

.. code:: python

    >>> github = GitHub(base_url="https://api.github.com/")
    >>> github.get_repos()
    <Response [200]>
    >>> _.url
    https://api.github.com/repositories


By default, uplink uses `Requests
<https://github.com/requests/requests>`_, so the response we get back
from GitHub is wrapped inside a :class:`requests.Response` instance.
(If you want, you can :ref:`swap out <_swap_default_http_client>` Requests for a
different backing HTTP client, such as :mod:`aiohttp <sync_vs_async>`.)


URL Manipulation
================

Resource endpoints can include `URI template parameters
<https://tools.ietf.org/html/rfc6570>`__ that depend on method
arguments. A simple URI parameter is an alphanumeric string surrounded
by ``{`` and ``}``.

To match the parameter with a method argument, either match the argument's
name with the alphanumeric string, like so:

.. code:: python

    @get("users/{username}")
    def get_user(self, username): pass

or use the :py:class:`~uplink.Path` annotation.

.. code:: python

    @get("users/{username}")
    def get_user(self, name: Path("username")): pass

:py:class:`~uplink.Query` parameters can also be added dynamically
by method arguments.

.. code:: python

    @get("users/{username}/repos")
    def get_repos(self, username, sort: Query): pass

For "catch-all" or complex query parameter combinations, a
:py:class:`~uplink.QueryMap` can be used:

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
parameters that need to be included with every request:

.. code:: python

    @params({"client_id": "my-client", "client_secret": "****"})
    class GitHub(Consumer):
        ...

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

A request header can depend on the value of a method argument by using
the :py:class:`~uplink.Header` function parameter annotation:

.. code:: python

    @get("user")
    def get_user(self, authorization: Header("Authorization"):
        """Get an authenticated user."""

Request Body
============

The :py:class:`~uplink.Body` annotation identifies a method argument as the
the HTTP request body:

.. code:: python

    @post("user/repos")
    def create_repo(self, repo: Body): pass

This annotation works well with the **keyword arguments** parameter (denoted
by the ``**`` prefix):

.. code:: python

    @post("user/repos")
    def create_repo(self, **repo_info: Body): pass

Moreover, this annotation is useful when using supported serialization
formats, such as :ref:`JSON <json>` and `Protocol Buffers
<https://github.com/prkumar/uplink-protobuf>`_. Take a look at
:ref:`this guide <serialization>` for more about serialization with Uplink.

.. _json:

Form Encoded, Multipart, and JSON Requests
==========================================

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

    @json
    @patch("user")
    def update_user(self, **user_info: uplink.Body):
        """Update an authenticated user."""

Alternatively, the :py:class:`~uplink.Field` annotation declares a JSON
field:

.. code:: python

    @json
    @patch("user")
    def update_user_bio(self, bio: Field):
        """Update the authenticated user's profile bio."""

Handling JSON Responses
=======================

Many modern public APIs serve JSON responses to their clients.

If your :class:`~uplink.Consumer` subclass accesses a JSON API, you can
decorate any method with :class:`returns.json <uplink.returns.json>` to
directly return the JSON response, instead of a response object, when
invoked:

.. code-block:: python

    class GitHub(Consumer):
        @returns.json
        @get("users/{username}")
        def get_user(self, username):
            """Get a single user."""

.. code-block:: python

    >>> github = GitHub("https://api.github.com")
    >>> github.get_user("prkumar")
    {'login': 'prkumar', 'id': 10181244, ...

When targeting a subset of the JSON response, you can use the
decorator's ``model`` argument to select the target JSON field name:

.. code-block:: python

    class GitHub(Consumer):
        @returns.json(member="blog")
        @get("users/{username}")
        def get_blog_url(self, username):
            """Get the user's blog URL."""

.. code-block:: python

    >>> github.get_blog_url("prkumar")
    "https://prkumar.io"

.. note::

    JSON responses may represent existing Python classes in your
    application (for example, a ``GitHubUser``). Uplink supports this
    kind of conversion (i.e., deserialization), and we detail this
    support in :ref:`this guide <serialization>`.


.. _`session`:

Persistence Across Requests from a :obj:`Consumer`
==================================================

.. versionadded:: 0.6.0

The :py:obj:`session` property of a :class:`~uplink.Consumer` instance exposes
the instance's configuration and allows for the persistence of certain
properties across requests sent from that instance.

You can provide default headers and query parameters for requests sent from a
consumer instance through its :py:obj:`session` property, like so:

.. code-block:: python

    class GitHub(Consumer):

        def __init__(self, username, password)
            # Creates the API token for this user
            api_key = create_api_key(username, password)

            # Send the API token as a query parameter with each request.
            self.session.params["api_key"] = api_key

        @get("user/repos")
        def get_user_repos(self, sort_by: Query("sort")):
            """Lists public repositories for the authenticated user."""

Headers and query parameters added through the :obj:`session` are
applied to all requests sent from the consumer instance.

.. code-block:: python

    github = GitHub("prkumar", "****")

    # Both `api_key` and `sort` are sent with the request.
    github.get_user_repos(sort_by="created")

Notably, in case of conflicts, the method-level headers and parameters
override the session-level, but the method-level properties are not
persisted across requests.

.. _`custom response handler`:

Response and Error Handling
===========================

You can intercept a response before it is returned (or deserialized) by using
the :class:`~uplink.response_handler` decorator:

.. code-block:: python

    def returns_success(response):
        return response.status == 200

    class GitHub(Consumer):
        @response_handler(returns_success)
        @json
        @post("user/repo")
        def create_repo(self, name: Field):
            """Create a new repository."""

You can :

.. code-block:: python

    @response_handler
    def returns_success(response):
        return response.status == 200





To register a custom response or error handler, decorate a function with
the :py:class:`response_handler` or :py:class:`error_handler` decorator.

.. note::

    Unlike consumer methods, these functions should be defined outside
    of a class scope.

For instance, the function :py:func:`returns_success` defined below is a
response handler that outputs whether or not the request was successful:

.. code-block:: python

    @response_handler
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
    class GitHub(Consumer):
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
    class TodoApp(Consumer):
        ...

.. _swap_default_http_client:

Swapping Out the Default HTTP Client
====================================

By default, Uplink sends requests using the Requests library. You can
configure the backing HTTP client using the :obj:`client` parameter of the
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