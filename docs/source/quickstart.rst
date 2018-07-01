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
from GitHub is wrapped within a :class:`requests.Response` instance.
(If you want, you can :ref:`swap out <sync_vs_async>` Requests for a
different backing HTTP client.)


URL Manipulation
================

Resource endpoints can include `URI template parameters
<https://tools.ietf.org/html/rfc6570>`__ that depend on method
arguments. A simple URI parameter is an alphanumeric string surrounded
by ``{`` and ``}``.

To match the parameter with a method argument, either match the argument's
name with the alphanumeric string, like so

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
<https://github.com/prkumar/uplink-protobuf>`_. We'll take a closer look at
serialization with Uplink in a later section.

.. _json:

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
