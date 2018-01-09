Introduction
************

Uplink delivers reusable and self-sufficient objects for accessing HTTP
webservices, with minimal code and user pain. Simply define your consumers
using decorators and function annotations, and we’ll handle
the rest for you... pun intended, obviously 😎

Static Request Handling
=======================

Method decorators describe request properties that are relevant
to all invocations of a consumer method.

For instance, consider the following GitHub API consumer:

.. code-block:: python
   :emphasize-lines: 2

   class GitHub(uplink.Consumer):
       @uplink.timeout(60)
       @uplink.get("/repositories")
       def get_repos(self):
           """Dump every public repository."""

Annotated with :py:class:`timeout`, the method :py:meth:`get_repos` will build
HTTP requests that wait an allotted number of seconds -- 60, in this case --
for the server to respond before giving up.

As method annotations are simply decorators, you can stack one on top of another
for chaining:

.. code-block:: python
   :emphasize-lines: 2,3

   class GitHub(uplink.Consumer):
       @uplink.headers({"Accept": "application/vnd.github.v3.full+json"})
       @uplink.timeout(60)
       @uplink.get("/repositories")
       def get_repos(self):
           """Dump every public repository."""

Dynamic Request Handling
========================

For programming in general, function parameters drive a function's
dynamic behavior; a function's output depends normally on its inputs.
With :py:mod:`uplink`, function arguments parametrize an HTTP request,
and you indicate the dynamic parts of the request by appropriately
annotating those arguments.

To illustrate, for the method :py:meth:`get_user` in the following
snippet, we have flagged the argument :py:attr:`username` as a URI
placeholder replacement using the :py:class:`~uplink.Path` annotation:

.. code-block:: python

    class GitHub(uplink.Consumer):
        @uplink.get("users/{username}")
        def get_user(self, username: uplink.Path("username")): pass

Invoking this method on a consumer instance, like so:

.. code-block:: python

    github.get_user(username="prkumar")

Builds an HTTP request that has a URL ending with ``users/prkumar``.

.. note::

    As you probably took away from the above example: when parsing the
    method's signature for argument annotations, :py:mod:`uplink` skips
    the instance reference argument, which is the leading method
    parameter and usually named :py:attr:`self`.