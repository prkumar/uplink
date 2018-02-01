Tips & Tricks
*************

Here are a few ways to simplify consumer definitions.

Decorating All Request Methods in a Class
=========================================

To apply a decorator across all methods in a class, you can simply
decorate the class rather than each method individually:

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
slightly more verbose definition:

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


Adopting the Argument's Name
============================

Several function argument annotations accept a :py:attr:`name` parameter
on construction. For instance, the :py:class:`~uplink.Path` annotation
uses the :py:attr:`name` parameter to associate the function argument to
a URI path parameter:

.. code-block:: python

    class GitHub(uplink.Consumer):
        @uplink.get("users/{username}")
        def get_user(self, username: uplink.Path("username")): pass

For such annotations, you can omit the :py:attr:`name` parameter to have the
annotation adopt the name of its corresponding method argument.

For instance, from the previous example, we can omit naming the
:py:class:`~uplink.Path` annotation since the corresponding argument's
name, :py:attr:`username`, matches the intended URI path parameter.

.. code-block:: python

    class GitHub(uplink.Consumer):
        @uplink.get("users/{username}")
        def get_user(self, username: uplink.Path): pass

Some annotations that support this behavior include:
:py:class:`~uplink.Path`, :py:class:`uplink.Field`, :py:class:`~uplink.Part`
:py:class:`~uplink.Header`, and :py:class:`uplink.Query`.

Annotating Your Arguments For Python 2.7
========================================

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
