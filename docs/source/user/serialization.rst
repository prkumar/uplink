.. _serialization:

Serialization
*************

Webservices use serialization formats to transmit structured data (a
list of repositories, a single user, a comment on a blog post, etc.)
over the network as a stream of bytes. For example, many modern public
APIs (e.g., `GitHub API v3 <https://developer.github.com/v3/>`_) support
JSON, while a private API used strictly within an organization may use a
more compact format, such as `Protocol Buffers
<https://developers.google.com/protocol-buffers/>`_.

Regardless what serialization format your API uses, with a little bit of
help, Uplink can automatically decode responses and encode request
bodies to and from Python objects using the selected format. This neatly
abstracts the HTTP layer from the callers of your API client.

This document walks you through how to leverage Uplink's serialization support,
including integrations for third-party serialization libraries like
:mod:`marshmallow` and tools for writing custom conversion strategy that
fit your unique needs.

Using Marshmallow Schemas
=========================

:mod:`marshmallow` is a framework-agnostic, object serialization library
for Python. Uplink comes with built-in support for Marshmallow; you can
integrate your Marshmallow schemas with Uplink for easy serialization.

First, create a :class:`marshmallow.Schema`, declaring any necessary
conversions and validations. Here's a simple example:

.. code-block:: python

   import marshmallow

   class RepoSchema(marshmallow.Schema):
       full_name = marshmallow.fields.Str()

       @marshmallow.post_load
       def make_repo(self, data):
           owner, repo_name = data["full_name"].split("/")
           return Repo(owner=owner, name=repo_name)


Then, specify the schema using the :class:`uplink.returns` decorator:

.. code-block:: python
   :emphasize-lines: 2

   class GitHub(Consumer):
      @returns(RepoSchema(many=True))
      @get("users/{username}/repos")
      def get_repos(self, username):
         """Get the user's public repositories."""

Python 3 users can use a return type hint instead:

.. code-block:: python
   :emphasize-lines: 3

   class GitHub(Consumer):
      @get("users/{username}/repos")
      def get_repos(self, username) -> RepoSchema(many=True)
         """Get the user's public repositories."""

Your consumer should now return Python objects based on your Marshmallow
schema:

.. code-block:: python

   github = GitHub(base_url="https://api.github.com")
   print(github.get_repos("octocat"))
   # Output: [Repo(owner="octocat", name="linguist"), ...]

For a more complete example of Uplink's :mod:`marshmallow` support,
check out `this example on GitHub <https://github.com/prkumar/uplink/tree/master/examples/marshmallow>`_.

Custom Conversion
=================

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

Converting Collections
======================

This section is a work in progress!

Other Serialization Formats (e.g., Protocol Buffers)
====================================================

This section is a work in progress!
