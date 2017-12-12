Introduction
************

Uplink turns your HTTP API into a Python class.

.. code:: python

    import uplink

    class GitHub(uplink.Consumer):
        @uplink.get("users/{user}/repos")
        def list_repos(self, user):
            """Get a user's public repositories."""

To interact with the webservice, simply instantiate the class.

.. code:: python

    github = GitHub(base_url="https://api.github.com/")

Then, invoke the class method to execute an HTTP request to the remote
webserver.

.. code:: python

    repos = github.list_repos("octocat")

Uplink uses the powerful `Requests
<http://docs.python-requests.org/en/master/>`_ library by default. So, the
returned list of :py:obj:`repos` is simply a :py:class:`requests.Response`:

.. code-block:: python

   print(repos.json())
   # Output: [{'id': 18221276, 'name': 'git-consortium', ...

For sending non-blocking requests, Uplink comes with support for
:py:mod:`aiohttp` and :py:mod:`twisted`.

Use decorators and function annotations to describe the HTTP request:

* URL parameter replacement and query parameter support
* Convert responses into Python objects (e.g., using :py:mod:`marshmallow`)
* JSON, URL-encoded, and multipart request body and file upload

API Declaration
---------------

Decorators on the consumer methods and function annotations on its
parameters indicate how a request will be handled.

Request Method
~~~~~~~~~~~~~~

Every method must have an HTTP decorator that provides the request
method and relative URL. There are five built-in annotations: ``get``,
``post``, ``put``, ``patch`` and ``delete``. The relative URL of the
resource is specified in the decorator.

.. code:: python

    @get("users/list")

You can also specify query parameters in the URL.

.. code:: python

    @get("users/list?sort=desc")

URL Manipulation
~~~~~~~~~~~~~~~~

TODO: Figure out how to better present this

A request URL can be updated dynamically using replacement blocks and
parameters on the method. A replacement block is an alphanumeric string
surrounded by ``{`` and ``}``. A corresponding method parameter can be
named after the string:

.. code:: python

    @get("group/{id}/users")
    def group_list(self, id): pass

Alternatively, the corresponding method paramter can be annotated with
``Path`` using the same string:

.. code:: python

    @get("group/{id}/users")
    def group_list(self, group_id: Path("id")): pass

Query parameters can also be added.

.. code:: python

    @get("group/{id}/users")
    def group_list(self, group_id: Path("id"), sort: Query("sort")): pass

For complex query parameter combinations, a mapping can be used:

.. code:: python

    @get("group/{id}/users")
    def group_list(self, group_id: Path("id"), options: QueryMap): pass

Request Body
~~~~~~~~~~~~

An object can be specified for use as an HTTP request body with the
``Body`` annotation:

.. code:: python

    @post("users/new")
    def create_user(self, user: Body): pass

TODO: Word this better: The keywargs parameter, ``**kwargs`` works well
with the ``Body`` annotation:

.. code:: python

    @post("users/new")
    def create_user(self, **user_info: Body): pass

Form Encoded and Multipart
~~~~~~~~~~~~~~~~~~~~~~~~~~

Methods can also be declared to send form-encoded and multipart data.

Form-encoded data is sent when ``form_url_encoded`` decorates the
method. Each key-value pair is annotated with ``Field``, containing the
name and the object providing the value.

.. code:: python

    @form_url_encoded
    @post("user/edit")
    def update_user(self, first_name: Field, last_name: Field): pass

Multipart requests are used when ``multipart`` decorates the method.
Parts are declared using the ``Part`` annotation:

.. code:: python

    @multipart
    @put("user/photo")
    def update_user(self, photo: Part, description: Part): pass

TODO: Mention that parts should be given as Requests expects them

Header Manipulation
~~~~~~~~~~~~~~~~~~~

You can set static headers for a method using the ``headers`` decorator.

.. code:: python

    @headers("Cache-Control: max-age=640000")
    @get("widget/list")
    def widget_list(): pass

.. code:: python

    @headers({
        "Accept": "application/vnd.github.v3.full+json",
        "User-Agent": "Uplink-Sample-App"
    })
    @get("users/{username}")
    def get_user(self, username): pass

Headers that need to added to every request can be specified by
decorating the consumer class.

Synchronous vs. Asynchronous
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TODO: talk about support with


Uplink delivers reusable and self-sufficient objects for accessing
HTTP webservices, with minimal code and user pain.

Defining similar objects with other Python HTTP clients, such as
:code:`requests`, often requires writing boilerplate code and layers of
abstraction. With Uplink, simply define your consumers using
decorators and function annotations, and we'll handle the REST for you! (Pun
intended, obviously.) 😎

**Method Annotations**: Static Request Handling
===============================================

Essentially, method annotations describe request properties that are relevant
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

Applying Multiple Method Annotations
------------------------------------

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

A Shortcut for Annotating All Methods in a Class
------------------------------------------------

To apply an annotation across all methods in a class, you can simply
annotate the class rather than each method individually:

.. code-block:: python
   :emphasize-lines: 1,2

    @uplink.timeout(60)
    class GitHub(uplink.Consumer):
        @uplink.get("/repositories")
        def get_repos(self):
            """Dump every public repository."""

        @uplink.get("/organizations")
        def get_organizations(self):
            """List all organizations."""

Hence, the consumer defined above is equivalent to the following,
slightly more verbose one:

.. code-block:: python

    class GitHub(uplink.Consumer):
        @uplink.timeout(60)
        @uplink.get("/repositories")
        def get_repos(self):
            """Dump every public repository."""

        @uplink.timeout(60)
        @uplink.get("/organizations")
        def get_organizations(self):
            """List all organizations."""

**Arguments Annotations**: Dynamic Request Handling
===================================================

In programming, parametrization drives a function's dynamic behavior; a
function's output depends normally on its inputs. With
:py:mod:`uplink`, function arguments parametrize an HTTP request, and
you indicate the dynamic parts of the request by appropriately
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

Adopting the Argument's Name
----------------------------

When you initialize a named annotation, such as a
:py:class:`~uplink.Path` or :py:class:`~Field`, without a name (by
omitting the :py:attr:`name` parameter), it adopts the name of its
corresponding method argument.

For example, in the snippet below, we can omit naming the
:py:class:`~uplink.Path` annotation since the corresponding argument's
name, :py:attr:`username`, matches the intended URI path parameter:

.. code-block:: python

    class GitHub(uplink.Consumer):
        @uplink.get("users/{username}")
        def get_user(self, username: uplink.Path): pass

Annotating Your Arguments
-------------------------

There are several ways to annotate arguments. Most examples in this
documentation use function annotations, but this approach is unavailable
for Python 2.7 users. Instead, you can use argument annotations as decorators
or utilize the method annotation :py:class:`~uplink.args`.

Argument Annotations as Decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For one, annotations can work as function decorators. With this approach,
annotations are mapped to arguments from "bottom-up".

For instance, in the below definition, the :py:class:`~uplink.Url`
annotation corresponds to :py:attr:`commits_url`, and
:py:class:`~uplink.Path` to :py:attr:`sha`.

.. code-block:: python
   :emphasize-lines: 2,3

    class GitHub(uplink.Consumer):
        @uplink.Path
        @uplink.Url
        @uplink.get
        def get_commit(self, commits_url, sha): pass

Using :py:class:`uplink.args`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The second approach involves using the method annotation
:py:class:`~uplink.args`, arranging annotations in the same order as
their corresponding function arguments (again, ignore :py:attr:`self`):

.. code-block:: python
   :emphasize-lines: 2

    class GitHub(uplink.Consumer):
        @uplink.args(uplink.Url, uplink.Path)
        @uplink.get
        def get_commit(self, commits_url, sha): pass

Function Annotations (Python 3 only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally, when using Python 3, you can use these classes as function
annotations (:pep:`3107`):

.. code-block:: python
   :emphasize-lines: 3

    class GitHub(uplink.Consumer):
        @uplink.get
        def get_commit(self, commit_url: uplink.Url, sha: uplink.Path):
            pass

Integration with :code:`python-requests`
========================================

Experienced users of `Kenneth Reitz's <https://github.com/kennethreitz>`__
well-established `Requests library <https://github
.com/requests/requests>`__ might be happy to read that Uplink uses
:py:mod:`requests` behind-the-scenes and bubbles :py:class:`requests.Response`
objects back up to the user.

Notably, Requests makes blocking calls. Users can swap out Requests for
an HTTP client library that supports asynchronous requests. Checkout
:ref:`non-blocking requests` to learn more about Uplink's support for
asynchronous requests.
