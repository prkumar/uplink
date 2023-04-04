.. _serialization:

Serialization
*************

Various serialization formats exist for transmitting structured data
over the network: JSON is a popular choice amongst many public APIs
partly because its human readable, while a more compact format, such as
`Protocol Buffers <https://developers.google.com/protocol-buffers/>`_,
may be more appropriate for a private API used within an organization.

Regardless what serialization format your API uses, Uplink -- with a
little bit of help -- can automatically decode responses and encode
request bodies to and from Python objects using the selected format.
This neatly abstracts the HTTP layer from your API client, so callers
can operate on objects that make sense to your model instead of directly
dealing with the underlying protocol.

This document walks you through how to leverage Uplink's serialization support,
including integrations for third-party serialization libraries like
:mod:`marshmallow`, :mod:`pydantic` and tools for writing custom conversion strategies that
fit your unique needs.

.. _using_marshmallow_schemas:

Using Marshmallow Schemas
=========================

:mod:`marshmallow` is a framework-agnostic, object serialization library
for Python. Uplink comes with built-in support for Marshmallow; you can
integrate your Marshmallow schemas with Uplink for easy JSON (de)serialization.

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


Then, specify the schema using the :class:`@returns <uplink.returns>` decorator:

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

.. _using_pydantic_schemas:

Using Pydantic Models
=========================

:mod:`pydantic` is a framework-agnostic, object serialization library
for Python >= 3.6. Uplink comes with built-in support for Pydantic; you can
integrate your Pydantic models with Uplink for easy JSON (de)serialization.

First, create a :class:`pydantic.BaseModel`, declaring any necessary
conversions and validations. Here's a simple example:

.. code-block:: python

   from typing import List

   from pydantic import BaseModel, HttpUrl

   class Owner(BaseModel):
      id: int
      avatar_url: HttpUrl
      organizations_url: HttpUrl

   class Repo(BaseModel):
      id: int
      full_name: str
      owner: Owner

Then, specify the schema using the :class:`@returns <uplink.returns>` decorator:

.. code-block:: python
   :emphasize-lines: 2

   class GitHub(Consumer):
      @returns.json(List[Repo])
      @get("users/{username}/repos")
      def get_repos(self, username):
         """Get the user's public repositories."""

Python 3 users can use a return type hint instead:

.. code-block:: python
   :emphasize-lines: 3

   class GitHub(Consumer):
      @returns.json()
      @get("users/{username}/repos")
      def get_repos(self, username) -> List[Repo]:
         """Get the user's public repositories."""

Your consumer should now return Python objects based on your Pydantic
model:

.. code-block:: python

   github = GitHub(base_url="https://api.github.com")
   print(github.get_repos("octocat"))
   # Output: [User(id=132935648, full_name='octocat/boysenberry-repo-1', owner=Owner(...), ...]

.. note::

   You may have noticed the usage of `returns.json` in both examples. Unlike :mod:`marshmallow`, :mod:`pydantic`
   has no `many` parameter to control the deserialization of multiple objects. The recommended approach
   is to use `returns.json` instead of defining a new model with a `__root__` element.

Serializing Method Arguments
============================

Most method argument annotations like :class:`~uplink.Field` and
:class:`~uplink.Body` accept a :obj:`type` parameter that specifies the
method argument's expected type or schema, for the sake of
serialization.

For example, following the :mod:`marshmallow` example from above, we can
specify the :class:`RepoSchema` as the :obj:`type` of a
:class:`~uplink.Body` argument:

.. code-block:: python

   from uplink import Consumer, Body

   class GitHub(Consumer):
      @json
      @post("user/repos")
      def create_repo(self, repo: Body(type=RepoSchema)):
         """Creates a new repository for the authenticated user."""

Then, the :obj:`repo` argument should accept instances of :class:`Repo`,
to be serialized appropriately using the :class:`RepoSchema` with
Uplink's :mod:`marshmallow` integration (see
:ref:`using_marshmallow_schemas` for the full setup).

.. code-block:: python

   repo = Repo(name="my_favorite_new_project")
   github.create_repo(repo)

The sample code above using :mod:`marshmallow` is also reproducible using :mod:`pydantic`:

.. code-block:: python

   from uplink import Consumer, Body

   class CreateRepo(BaseModel):
      name: str
      delete_branch_on_merge: bool

   class GitHub(Consumer):
      @post("user/repos")
      def create_repo(self, repo: Body(type=CreateRepo)):
         """Creates a new repository for the authenticated user."""

Then, calling the client.

.. code-block:: python
   repo = CreateRepo(name="my-new-uplink-pydantic", delete_branch_on_merge=True)
   github.create_repo(repo)

.. _custom_json_deserialization:

Custom JSON Conversion
======================

Recognizing JSON's popularity amongst public APIs, Uplink provides
some out-of-the-box utilities that make adding JSON serialization support for
your objects simple.

Deserialization
---------------

:class:`@returns.json <uplink.returns.json>` is handy when working with
APIs that provide JSON responses. As its leading positional argument, the decorator
accepts a class that represents the expected schema of the JSON response body:

.. code-block:: python
   :emphasize-lines: 2

   class GitHub(Consumer):
       @returns.json(User)
       @get("users/{username}")
       def get_user(self, username): pass

Python 3 users can alternatively use a return type hint:

.. code-block:: python
   :emphasize-lines: 4

    class GitHub(Consumer):
       @returns.json
       @get("users/{username}")
       def get_user(self, username) -> User: pass

Next, if your objects (e.g., :py:obj:`User`) are not defined
using a library for which Uplink has built-in support (such as
:py:mod:`marshmallow`), you will also need to register a converter that
tells Uplink how to convert the HTTP response into your expected return
type.

To this end, we can use :py:meth:`@loads.from_json <uplink.loads.from_json>`
to define a simple JSON reader for :class:`User`:

.. code-block:: python

   from uplink import loads

    @loads.from_json(User)
    def user_json_reader(user_cls, json):
        return user_cls(json["id"], json["username"])

The decorated function, :py:func:`user_json_reader`, can then be passed into the
:py:attr:`converter` constructor parameter when instantiating a
:py:class:`uplink.Consumer` subclass:

.. code-block:: python

    github = GitHub(base_url=..., converter=user_json_reader)

Alternatively, you can add the :py:func:`@uplink.install <uplink.install>` decorator to
register the converter function as a default converter, meaning the converter
will be included automatically with any consumer instance and doesn't need to
be explicitly provided through the :py:obj:`converter` parameter:

.. code-block:: python
   :emphasize-lines: 1

   from uplink import loads, install

    @install
    @loads.from_json(User)
    def user_json_reader(user_cls, json):
        return user_cls(json["id"], json["username"])

At last, calling the :meth:`GitHub.get_user` method should now return an
instance of our :class:`User` class:

.. code-block:: python

   github.get_user("octocat")
   # Output: [User(id=583231, name="The Octocat"), ...]

Serialization
-------------

:class:`@json <uplink.json>` is a decorator for :class:`~uplink.Consumer`
methods that send JSON requests. Using this decorator requires annotating
your arguments with either :class:`~uplink.Field` or :class:`~uplink.Body`.
Both annotations support an optional :obj:`type` argument for the purpose
of serialization:

.. code-block:: python
   :emphasize-lines: 6

   from uplink import Consumer, Body

   class GitHub(Consumer):
      @json
      @post("user/repos")
      def create_repo(self, user: Body(type=Repo)):
         """Creates a new repository for the authenticated user."""

Similar to deserialization case, we must register a converter that tells
Uplink how to turn the :py:obj:`Repo` object to JSON, since the class
is not defined using a library for which Uplink has built-in support
(such as :py:mod:`marshmallow`).

To this end, we can use :py:meth:`@dumps.to_json <uplink.dumps.to_json>`
to define a simple JSON writer for :class:`Repo`:

.. code-block:: python

   from uplink import dumps

    @dumps.to_json(Repo)
    def repo_json_writer(repo_cls, repo):
        return {"name": repo.name, "private": repo.is_private()}

The decorated function, :py:func:`repo_json_writer`, can then be passed into the
:py:attr:`converter` constructor parameter when instantiating a
:py:class:`uplink.Consumer` subclass:

.. code-block:: python

    github = GitHub(base_url=..., converter=repo_json_writer)

Alternatively, you can add the :py:func:`@uplink.install <uplink.install>` decorator to
register the converter function as a default converter, meaning the converter
will be included automatically with any consumer instance and doesn't need to
be explicitly provided through the :py:obj:`converter` parameter:

.. code-block:: python
   :emphasize-lines: 1

   from uplink import loads, install

    @install
    @dumps.to_json(Repo)
    def repo_json_writer(user_cls, json):
        return {"name": repo.name, "private": repo.is_private()}

Now, we should be able to invoke the :meth:`GitHub.create_repo` method
with an instance of :class:`Repo`:

.. code-block:: python

   repo = Repo(name="my_new_project", private=True)
   github.create_repo(repo)

.. _converting_collections:

Converting Collections
======================

Data-driven web applications, such as social networks and forums, devise
a lot of functionality around large queries on related data. Their APIs
normally encode the results of these queries as collections of a common
**type**. Examples include a curated feed of **posts** from subscribed
accounts, the top **restaurants** in your area, upcoming *tasks** on a
checklist, etc.

You can use the other strategies in this section to add serialization
support for a specific type, such as a **post** or a **restaurant**.
Once added, this support automatically extends to collections of that
type, such as sequences and mappings.

For example, consider a hypothetical Task Management API that supports
adding tasks to one or more user-created checklists. Here's the JSON
array that the API returns when we query pending tasks on a checklist
titled "home":

.. code-block:: json

  [
      {
         "id": 4139
         "name": "Groceries"
         "due_date": "Monday, September 3, 2018 10:00:00 AM PST"
      },
      {
         "id": 4140
         "name": "Laundry"
         "due_date": "Monday, September 3, 2018 2:00:00 PM PST"
      }
  ]

In this example, the common type could be modeled in Python as a
:class:`~collections.namedtuple`, which we'll name :class:`Task`:

.. code-block:: python

   Task = collections.namedtuple("Task", ["id", "name", "due_date"])

Next, to add JSON deserialization support for this type, we could
create a custom converter using the :meth:`@loads.from_json
<uplink.loads.from_json>` decorator, which is a strategy covered in the
subsection :ref:`custom_json_deserialization`. For the sake of brevity,
I'll omit the implementation here, but you can follow the link above for
details.

Notably, Uplink lets us leverage the added support to also handle
collections of type :class:`Task`. The :mod:`uplink.types` module
exposes two collection types, :data:`~uplink.List` and
:data:`~uplink.types.Dict`, to be used as function return type
annotations. In our example, the query for pending tasks returns a list:

.. code-block:: python
   :emphasize-lines: 6

   from uplink import Consumer, returns, get, types

   class TaskApi(Consumer):
      @returns.json
      @get("tasks/{checklist}?due=today")
      def get_pending_tasks(self, checklist) -> types.List[Task]

If you are a Python 3.5+ user that is already leveraging the
:mod:`typing` module to support type hints as specified by :pep:`484`
and :pep:`526`, you can safely use :class:`typing.List` and :class:`typing.Dict`
here instead of the annotations from :mod:`uplink.types`:

.. code-block:: python
   :emphasize-lines: 7

   import typing
   from uplink import Consumer, returns, get

   class TaskApi(Consumer):
      @returns.json
      @get("tasks/{checklist}?due=today")
      def get_pending_tasks(self, checklist) -> typing.List[Task]

Now, the consumer can handle these queries with ease:

.. code-block:: python

   >>> task_api.get_pending_tasks("home")
   [Task(id=4139, name='Groceries', due_date='Monday, September 3, 2018 10:00:00 AM PST'),
    Task(id=4140, name='Laundry', due_date='Monday, September 3, 2018 2:00:00 PM PST')]

Note that this feature works with any serialization format, not just JSON.

Writing A Custom Converter
==========================

Extending Uplink's support for other serialization formats or libraries
(e.g., XML, Thrift, Avro) is pretty straightforward.

When adding support for a new serialization library, create a subclass
of :class:`converters.Factory <uplink.converters.Factory>`, which
defines abstract methods for different serialization scenarios
(deserializing the response body, serializing the request body, etc.),
and override each relevant method to return a callable that
handles the method's corresponding scenario.

For example, a factory that adds support for Python's :mod:`pickle` protocol
could look like:

.. code-block:: python

   import pickle

   from uplink import converters

   class PickleFactory(converters.Factory):
      """Adapter for Python's Pickle protocol."""

      def create_response_body_converter(self, cls, request_definition):
         # Return callable to deserialize response body into Python object.
         return lambda response: pickle.loads(response.content)

      def create_request_body_converter(self, cls, request_definition):
         # Return callable to serialize Python object into bytes.
         return pickle.dumps

Then, when instantiating a new consumer, you can supply this
implementation through the ``converter`` constructor argument of any
:class:`Consumer` subclass:

.. code-block:: python

   client = MyApiClient(BASE_URL, converter=PickleFactory())

If the added support should apply broadly, you can alternatively decorate your
:class:`converters.Factory <uplink.converters.Factory>` subclass with
the :meth:`@uplink.install <uplink.install>` decorator, which ensures that Uplink
automatically adds the factory to new instances of any
:class:`Consumer` subclass. This way you don't have to explicitly supply
the factory each time you instantiate a consumer.

.. code-block:: python
   :emphasize-lines: 3

   from uplink import converters, install

   @install
   class PickleFactory(converters.Factory):
      ...

For a concrete example of extending support for a new serialization
format or library with this approach, checkout `this Protobuf extension
<https://github.com/prkumar/uplink-protobuf/blob/master/uplink_protobuf/converter.py>`_
for Uplink.
