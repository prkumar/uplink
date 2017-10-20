Getting Started
***************

In this section, we'll cover the basics with Uplink. To illustrate usage
with an existent service, we mainly provide examples with GitHub's API.
To try them out yourself, you can simply copy the code snippets into a
script or the Python console.

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

As illustrated in the previous example, to create consumer instances, use the
:py:func:`uplink.build` function. Notably, this helper function affords us
the ability to reuse consumers in different contexts.

For instance, by simply changing the function's :py:attr:`base_url`
parameter, we could use the same GitHub API consumer against the main
website, ``github.com``, and any GitHub Enterprise instance, since they
offer identical APIs.

Setting the URL
===============

To set a **static URL**, use the the leading parameter, :py:attr:`path`,
of the HTTP method decorator:

.. code-block:: python
   :emphasize-lines: 2

    class GitHub(object):
        @uplink.get("/repositories")
        def get_repos(self): pass

Alternatively, you can provide the URL at runtime as a method argument.
To set a **dynamic URL**, omit the decorator parameter :py:attr:`path`
and annotate the corresponding method argument with
:py:class:`uplink.Url`:

.. code-block:: python
   :emphasize-lines: 3

    class GitHub(object);
        @uplink.get
        def get_commit(self, commit_url: uplink.Url): pass

.. _path_variables:

Path Variables
==============

For both static and dynamic URLs, Uplink supports `URI
templates <https://tools.ietf.org/html/rfc6570>`__. These
templates can contain parameters enclosed in braces (e.g., :code:`{name}`)
for method arguments to handle at runtime.

To map a method argument to a declared URI path parameter for expansion, use
the :py:class:`uplink.Path` annotation. For instance, we can define a consumer
method to query any GitHub user's metadata by declaring the
`path segment parameter <https://tools.ietf.org/html/rfc6570#section-3.2.6>`__
:code:`{/username}` in the method's URL.

.. code-block:: python

    class GitHub(object):
        @get("users{/username}")
        def get_user(self, username: Path("username")): pass

With an instance of this consumer, we can invoke the :code:`get_user`
method like so

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
        @uplink.get("users{/username}")
        def get_user(self, username): pass

Important to note, failure to resolve all unannotated function arguments
raises an :py:class:`~uplink.InvalidRequestDefinitionError`.

Query Parameters
================

To set unchanging query parameters, you can append a query string to the
static URL. For instance, GitHub offers the query parameter :code:`q`
for adding keywords to a search. With this, we can define a consumer
that queries all GitHub repositories written in Python:

.. code-block:: python
   :emphasize-lines: 2

    class GitHub(object):
        @uplink.get("/search/repositories?q=language:python")
        def search_python_repos(self): pass

Note that we have hard-coded the query parameter into the URL, so that all
requests that this method handles include that search term.

Alternatively, we can set query parameters at runtime using method
arguments. To set dynamic query parameters, use the :py:class:`uplink.Query` and
:py:class:`uplink.QueryMap` argument annotations.

For instance, to set the search term :code:`q` at runtime, we can
provide a method argument annotated with :py:class:`uplink.Query`:

.. code-block:: python
   :emphasize-lines: 3

    class GitHub(object):
        @uplink.get("/search/repositories")
        def search_repos(self, q: uplink.Query)

Further, the :py:class:`uplink.QueryMap` annotation indicates that an
argument handles a mapping of query parameters. For example, let's use this
annotation to transform keyword arguments into query parameters:

.. code-block:: python
   :emphasize-lines: 3

   class GitHub(object):
       @uplink.get("/search/repositories")
       def search_repos(self, **params: uplink.QueryMap)

This serves as a nice alternative to adding a :py:class:`uplink.Query`
annotated argument for each supported query parameter. For instance,
we can now optionally modify how the GitHub search results are sorted,
leveraging the :code:`sort` query parameter:

.. code-block:: python

    # Search for Python repos and sort them by number of stars.
    github.search_repos(q="language:python", sort="stars").execute()

.. note::

    Another approach for setting dynamic query parameters is to use `path
    variables`_ in the static URL, with `"form-style query expansion"
    <https://tools ietf org/html/rfc6570#section-3.2.8>`_.

HTTP Headers
============

To add literal headers, use the :py:class:`uplink.headers` method annotation,
which has accepts the input parameters as :py:class:`dict`:

.. code-block:: python
   :emphasize-lines: 2,3

    class GitHub(object):
        # This header explicitly requests version v3 of the GitHub API.
        @uplink.headers({"Accept": "application/vnd.github.v3.full+json"})
        @uplink.get("/repositories")
        def get_repos(self): pass

Alternatively, we can use the :py:class:`uplink.Header` argument annotation to
pass a header as a method argument at runtime:

.. code-block:: python
   :emphasize-lines: 6

    class GitHub(object):
        @uplink.get("/users{/username}")
        def get_user(
            self,
            username,
            last_modified: uplink.Header("If-Modified-Since")
        ):
            """Fetch a GitHub user if modified after given date."""

Further, you can annotate an argument with :py:class:`uplink.HeaderMap` to
accept a mapping of header fields.

URL-Encoded Request Body
========================

For ``POST``/``PUT``/``PATCH`` requests, the format of the message body
is an important detail. A common approach is to url-encode the body and
set the header ``Content-Type: application/x-www-form-urlencoded``
to notify the server.

To submit a url-encoded form with Uplink, decorate the consumer method
with :py:class:`uplink.form_url_encoded` and annotate each argument
accepting a form field with :py:class:`uplink.Field`. For instance,
let's provide a method for reacting to a specific GitHub issue:

.. code-block:: python
   :emphasize-lines: 2,7

    class GitHub(object):
        @uplink.form_url_encoded
        @uplink.patch("/user")
        def update_blog_url(
            self,
            access_token: uplink.Query,
            blog_url: uplink.Field
        ):
            """Update a user's blog URL."""

Further, you can annotate an argument with :py:class:`uplink.FieldMap` to
accept a mapping of form fields.

Send Multipart Form Data
========================

`Multipart requests
<https://en.wikipedia.org/wiki/MIME#Multipart_messages>`__ are commonly
used to upload files to a server.

To send a multipart message, decorate a consumer method with
:py:class:`uplink.multipart`. Moreover, use the :py:class:`uplink.Part` argument
annotation to mark a method argument as a form part.

.. todo::

   Add a code block that illustrates an example of how to define a
   consumer method that sends multipart requests.

Further, you can annotate an argument with :py:class:`uplink.PartMap` to
accept a mapping of form fields to parts.

JSON Requests, and Other Content Types
======================================

Nowadays, many HTTP webservices nowadays accept JSON requests. (GitHub's
API is an example of such a service.) Given the format's growing
popularity, Uplink provides the decorator :py:class:`uplink.json`.

When using this decorator, you should annotate a method argument with
:py:class:`uplink.Body`, which indicates that the argument's value
should become the request's body. Moreover, this value is expected to be
an instance of :py:class:`dict` or a subclass of
:py:class:`uplink.Mapping`.

Note that :py:class:`uplink.Body` can annotate the keyword argument, which
often enables concise method signatures:

.. code-block:: python
   :emphasize-lines: 2,7

    class GitHub(object):
        @uplink.json
        @uplink.patch("/user")
        def update_user(
            self,
            access_token: uplink.Query,
            **info: uplink.Body
        ):
            """Update an authenticated user."""


Further, you may be able to send other content types by using
:py:class:`uplink.Body` and setting the ``Content-Type`` header
appropriately with the decorator :py:class:`uplink.header`.