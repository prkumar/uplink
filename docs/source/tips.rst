Tips & Tricks
*************

Here are a few ways to simplify consumer definitions.

Decorating All Request Methods in a Class
=========================================

To apply an decorator across all methods in a class, you can simply
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
slightly more verbose alternative:

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
