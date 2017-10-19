Getting Started
***************

Uplink

Making a Request
================

The simplest API consumer method requires only an HTTP method decorator.

For example, let's define an GitHub API consumer that can retrieve all the
public repositories hosted on the site:

.. code-block:: python

    import uplink

    class GitHub(object):
        @uplink.get("/repositories")
        def get_repos(self): pass

Now, to fetch the list of public repositories hosted on :code:`github.com`,
we simply invoke the :py:meth:`get_repos` with a consumer instance:

.. code-block:: python

    github = uplink.build(GitHub, base_url="https://api.github.com")
    response = github.get_repos().execute()
    print(response.json()) # [{u'issues_url': u'https://api.github.com/repos/mojombo/grit/issues{/number}', ...

To summarize, we used the :py:class:`get` decorator to indicate that the
:py:meth:`get_repos` method handles an HTTP ``GET`` request targeting the
:code:`/repositories` endpoint.

Further, Uplink currently supports :py:class:`~uplink.get`,
:py:class:`~uplink.post`, :py:class:`~uplink.put`, :py:class:`~uplink.patch`,
and :py:class:`~uplink.delete`.

Creating Consumer Instances with :code:`uplink.build`
-----------------------------------------------------

To create consumer instances, use the :py:func:`uplink.build` function.
Notably, this helper function affords us the ability to reuse consumers in
different contexts.

For instance, by simply changing the function's :py:attr:`base_url`
parameter, we could use the consumer defined in the previous example,
:py:attr:`GitHub`, also against any GitHub Enterprise instance, since these
services offer an API identical to that of the main website.

Setting the URL
===============

To set a **static URL**, simply use the the first parameter, :py:attr:`path`,
of the HTTP method decorator:

.. code-block:: python
   :emphasize-lines: 2

    class GitHub(object):
        @uplink.get("/repositories")
        def get_repos(self): pass

Alternatively, you can allow users to pass the URL at runtime as a
method argument. To set a **dynamic URLs**, omit the decorator parameter
:code:`path` and annotate the corresponding method argument with
:py:class:`uplink.Url`:

.. code-block:: python
   :emphasize-lines: 3

    class GitHub(object);
        @uplink.get
        def get_commit(self, commit_url: uplink.Url): pass

Path Variables
==============

For both static and dynamic URLs, Uplink supports `URI
templates <https://tools.ietf.org/html/rfc6570>`__. These
templates can contain parameters enclosed in braces (e.g., :code:`{name}`)
for method arguments to handle.

To map a method argument to a declared URI path parameter for expansion, use
the :py:class:`uplink.Path` annotation:

.. code-block:: python

    class GitHub(object):
        @get("users/{username}")
        def get_user(self, username: Path("username")): pass

With an instance of the above defined consumer, we can invoke the
:code:`get_user` method like so

.. code-block:: python

    github.get_user("prkumar")

to create an HTTP request with a URL ending in :code:`users/prkumar`.

.. _implicit_path_annotations:


Implicit :code:`Path` Annotations
----------------------------------

When building the consumer instance, :py:func:`uplink.build` will try to resolve
unannotated method arguments by matching their names with URI path parameters.

For example, consider the consumer defined below, in which the method
:py:meth:`get_user` has an unannotated argument, :py:attr:`username`.
Since its name matches the URI path parameter ``{username}``,
:py:mod:`uplink` will auto-annotate the argument with :py:class:`Path`
for us:

.. code-block:: python

    class GitHub(object):
        @uplink.get("user/{username}")
        def get_user(self, username): pass

Important to note, failure to resolve all unannotated function arguments
raises an :py:class:`~uplink.InvalidRequestDefinitionError`.

Query Parameters
================

HTTP Headers
============

URL-Encoded Request Body
========================

Send Multipart Form Data
========================

JSON Requests, and Other Content Types
======================================







