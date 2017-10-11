Introduction
************

**Method Annotations**: Static Request Properties
=================================================

Essentially, method annotations describe Request properties that are relevant
to all invocations of a consumer method.

For instance, consider the following GitHub API consumer:

.. code-block:: python
   :emphasize-lines: 2

   class GitHubService(object):
       @uplink.timeout(60)
       @uplink.get("/repositories")
       def get_repos(self):
           """Dump every public repository."""



Annotated with :py:class:`timeout`, the method :py:meth:`get_repos` will build
HTTP requests that wait an allotted number of seconds -- 60, in this case --
for the server to respond before giving up.

As method annotations are simply decorators, you can stack one on top of another
to chain them.


A Shortcut for Annotating All Methods in a Class
------------------------------------------------

To apply an annotation across all methods in a class, you can simply
annotate the class rather than each method individually:

.. code-block:: python
   :emphasize-lines: 1,2

    @uplink.timeout(60)
    class GitHubService(object):
        @uplink.get("/repositories")
        def get_repos(self):
            """Dump every public repository."""

        @uplink.get("/organizations")
        def get_organizations(self):
            """List all organizations."""


Let's drive this point home; the consumer defined above is equivalent to
the following, slightly more verbose one:

.. code-block:: python

    class GitHubService(object):
        @uplink.timeout(60)
        @uplink.get("/repositories")
        def get_repos(self):
            """Dump every public repository."""

        @uplink.timeout(60)
        @uplink.get("/organizations")
        def get_organizations(self):
            """List all organizations."""



**Arguments Annotations**: Dynamic Request Properties
=====================================================

In programming, parametrization drives a function's dynamic behavior; a
function's output depends normally on its inputs. With
:py:mod:`uplink`, function arguments parametrize an HTTP request, and
you indicate the dynamic parts of the request by appropriately
annotating those arguments.

To illustrate, for the method :py:meth:`get_user` in the following
snippet, we have flagged the argument :py:attr:`username` as a URI
placeholder replacement using the :py:class:`~uplink.Path` annotation:

.. code-block:: python

    class GitHubService(object):
        @uplink.get("users/{username}")
        def get_user(self, username: uplink.Path("username")): pass

Invoking this method on a consumer instance, like so:

.. code-block:: python

    github.get_user(username="prkumar")

Builds an HTTP request that has a URL ending with ``users/prkumar``.

.. note::
    As you probably took away from the above example, :py:mod:`uplink`
    ignores the instance reference argument (e.g., :py:attr:`self`), with
    respect to argument annotations.

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

    class GitHubService(object):
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

    class GitHubService(object):
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

    class GitHubService(object):
        @uplink.args(uplink.Url, uplink.Path)
        @uplink.get
        def get_commit(self, commits_url, sha): pass


Function Annotations (Python 3 only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally, when using Python 3, you can use these classes as function
annotations (:pep:`3107`):

.. code-block:: python
   :emphasize-lines: 3

    class GitHubService(object):
        @uplink.get
        def get_commit(self, commit_url: uplink.Url, sha: uplink.Path):
            pass