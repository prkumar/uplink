.. _quickstart:

Quickstart
**********

Ready to write your first API client with Uplink? This guide will
walk you through what you'll need to know to get started.

**First**, make sure you've :ref:`installed (or updated) Uplink <install>`:

::

    $ pip install -U uplink

Defining an API Client
======================

Writing a **structured** API client with Uplink is very simple.

To start, create a subclass of :class:`~uplink.Consumer`. For example,
here's the beginning of our GitHub client (we'll add some methods to
this class soon):

.. code-block:: python

   from uplink import Consumer

   class GitHub(Consumer):
      ...

When creating an instance of this consumer, we can use the :obj:`base_url`
constructor argument to identify the target service. In our case, it's
GitHub's public API:

.. code-block:: python

   github = GitHub(base_url="https://api.github.com/")

.. note::

    :obj:`base_url` is especially useful for creating clients that
    target separate services with similar APIs; for example, we could use
    this GitHub consumer to also create clients for any GitHub
    Enterprise instance for projects hosted outside of the public
    `GitHub.com <https://github.com>`_ service. Another example is
    creating separate clients for a company's production and staging
    environments, which are typically hosted on separate domains but
    expose the same API.

So far, this class looks like any other Python class. The real magic
happens when you define methods to interact with the webservice using
Uplink's HTTP method decorators, which we cover next.

Making a Request
================

With Uplink, making a request to a webservice is as simple as
invoking a method.

Any method of a :class:`Consumer` subclass can be
decorated with one of Uplink's HTTP method decorators:
:class:`@get <uplink.get>`, :class:`@post <uplink.post>`, :class:`@put <uplink.put>`,
:class:`@patch <uplink.patch>`, :class:`@head <uplink.head>`, and :class:`@delete <uplink.delete>`:

.. code-block:: python

    class GitHub(Consumer):
        @get("repositories")
        def get_repos(self):
            """List all public repositories."""

As shown above, the method's body can be left empty.

The decorator's first argument is the resource endpoint (this
is the relative URL path from :class:`base_url`, which we covered above):

.. code-block:: python

    @get("repositories")

You can also specify query parameters:

.. code-block:: python

    @get("repositories?since=364")

Finally, invoke the method to send a request:

.. code-block:: python

    >>> github = GitHub(base_url="https://api.github.com/")
    >>> github.get_repos()
    <Response [200]>
    >>> _.url
    https://api.github.com/repositories


By default, uplink uses `Requests
<https://github.com/requests/requests>`_, so the response we get back
from GitHub is wrapped inside a :class:`requests.Response` instance. (If
you want, you can :ref:`swap out <swap_default_http_client>`
Requests for a different backing HTTP client, such as :ref:`aiohttp <sync_vs_async>`.)

.. |aiohttp| replace:: ``aiohttp``

URL Manipulation
================

Resource endpoints can include `URI template parameters
<https://tools.ietf.org/html/rfc6570>`__ that depend on method
arguments. A simple URI parameter is an alphanumeric string surrounded
by ``{`` and ``}``.

To match the parameter with a method argument, either match the argument's
name with the alphanumeric string, like so:

.. code-block:: python

    @get("users/{username}")
    def get_user(self, username): pass

or use the :py:class:`~uplink.Path` annotation.

.. code-block:: python

    @get("users/{username}")
    def get_user(self, name: Path("username")): pass

:py:class:`~uplink.Query` parameters can also be added dynamically
by method arguments.

.. code-block:: python

    @get("users/{username}/repos")
    def get_repos(self, username, sort: Query): pass

For "catch-all" or complex query parameter combinations, a
:py:class:`~uplink.QueryMap` can be used:

.. code-block:: python

    @get("users/{username}/repos")
    def get_repos(self, username, **options: QueryMap): pass

You can set static query parameters for a method using the
:py:class:`@params <uplink.params>` decorator.

.. code-block:: python

    @params({"client_id": "my-client", "client_secret": "****"})
    @get("users/{username}")
    def get_user(self, username): pass

:py:class:`@params <uplink.params>` can be used as a class decorator for query
parameters that need to be included with every request:

.. code-block:: python

    @params({"client_id": "my-client", "client_secret": "****"})
    class GitHub(Consumer):
        ...

Header Manipulation
===================

You can set static headers for a method using the :py:class:`@headers <uplink.headers>`
decorator.

.. code-block:: python

    @headers({
        "Accept": "application/vnd.github.v3.full+json",
        "User-Agent": "Uplink-Sample-App"
    })
    @get("users/{username}")
    def get_user(self, username): pass

:py:class:`@headers <uplink.headers>` can be used as a class decorator for headers that
need to be added to every request:

.. code-block:: python

    @headers({
        "Accept": "application/vnd.github.v3.full+json",
        "User-Agent": "Uplink-Sample-App"
    })
    class GitHub(Consumer):
        ...

A request header can depend on the value of a method argument by using
the :py:class:`~uplink.Header` function parameter annotation:

.. code-block:: python

    @get("user")
    def get_user(self, authorization: Header("Authorization"):
        """Get an authenticated user."""

Request Body
============

The :py:class:`~uplink.Body` annotation identifies a method argument as the
the HTTP request body:

.. code-block:: python

    @post("user/repos")
    def create_repo(self, repo: Body): pass

This annotation works well with the **keyword arguments** parameter (denoted
by the ``**`` prefix):

.. code-block:: python

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

Form-encoded data is sent when :py:class:`@form_url_encoded <uplink.form_url_encoded>` decorates
the method. Each key-value pair is annotated with a :py:class:`~uplink.Field`
annotation:

.. code-block:: python

    @form_url_encoded
    @patch("user")
    def update_user(self, name: Field, email: Field): pass

Multipart requests are used when :py:class:`@multipart <uplink.multipart>` decorates the
method. Parts are declared using the :py:class:`~uplink.Part` annotation:

.. code-block:: python

    @multipart
    @put("user/photo")
    def upload_photo(self, photo: Part, description: Part): pass

JSON data is sent when :py:class:`@json <uplink.json>` decorates the method. The
:py:class:`~uplink.Body` annotation declares the JSON payload:

.. code-block:: python

    @json
    @patch("user")
    def update_user(self, **user_info: uplink.Body):
        """Update an authenticated user."""

Alternatively, the :py:class:`~uplink.Field` annotation declares a JSON
field:

.. code-block:: python

    @json
    @patch("user")
    def update_user_bio(self, bio: Field):
        """Update the authenticated user's profile bio."""

Handling JSON Responses
=======================

Many modern public APIs serve JSON responses to their clients.

If your :class:`~uplink.Consumer` subclass accesses a JSON API, you can
decorate any method with :class:`@returns.json <uplink.returns.json>` to
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

You can also target a specific field of the JSON response by using the
decorator's ``key`` argument to select the target JSON field name:

.. code-block:: python

    class GitHub(Consumer):
        @returns.json(key="blog")
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
    support in :ref:`the next guide <serialization>`.


.. _`session`:

Persistence Across Requests from a :obj:`Consumer`
==================================================

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

Sometimes, you need to validate a response before it is returned or
even calculate a new return value from the response. Or, you may need
to handle errors from the underlying client before they reach your
users.

With Uplink, you can address these concerns by registering a callback
with one of these decorators: :class:`@response_handler <uplink.response_handler>` and
:class:`@error_handler <uplink.error_handler>`.

:class:`@response_handler <uplink.response_handler>` registers a callback to intercept
responses before they are returned (or deserialized):

.. code-block:: python

    def raise_for_status(response):
        """Checks whether or not the response was successful."""
        if 200 <= response.status <= 299:
            raise UnsuccessfulRequest(response.url)

        # Pass through the response.
        return response

    class GitHub(Consumer):
        @response_handler(raise_for_status)
        @post("user/repo")
        def create_repo(self, name: Field):
            """Create a new repository."""

:class:`@error_handler <uplink.error_handler>` registers a callback to handle an
exception thrown by the underlying HTTP client
(e.g., :class:`requests.Timeout`):

.. code-block:: python

    def raise_api_error(exc_type, exc_val, exc_tb):
        """Wraps client error with custom API error"""
        raise MyApiError(exc_val)

    class GitHub(Consumer):
        @error_handler(raise_api_error)
        @post("user/repo")
        def create_repo(self, name: Field):
            """Create a new repository."""

To apply a handler onto all methods of a :py:class:`~uplink.Consumer`
subclass, you can simply decorate the class itself:

.. code-block:: python

    @error_handler(raise_api_error)
    class GitHub(Consumer):
        ...

Notably, the decorators can be stacked on top of one another to chain their
behaviors:

.. code-block:: python

    @response_handler(check_expected_headers)  # Second, check headers
    @response_handler(raise_for_status)  # First, check success
    class GitHub(Consumer):
        ...

Lastly, both decorators support the optional argument
:obj:`requires_consumer`. When this option is set to :obj:`True`, the
registered callback should accept a reference to the :class:`~Consumer`
instance as its leading argument:

.. code-block:: python
   :emphasize-lines: 1-2, 11

    @error_handler(requires_consumer=True)
    def raise_api_error(consumer, exc_type, exc_val, exc_tb):
        """Wraps client error with custom API error"""
        ...

    class GitHub(Consumer):
        @raise_api_error
        @post("user/repo")
        def create_repo(self, name: Field):
            """Create a new repository."""
