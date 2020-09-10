Converters
**********

The :py:obj:`converter` parameter of the :py:class:`uplink.Consumer`
constructor accepts a custom adapter class that handles serialization of
HTTP request properties and deserialization of HTTP response objects:

.. code-block:: python

    github = GitHub(BASE_URL, converter=...)


Starting with version v0.5, some out-of-the-box converters are included
automatically and don't need to be explicitly provided through the
``converter`` parameter. These implementations are detailed below.


Marshmallow
===========

Uplink comes with optional support for :py:mod:`marshmallow`.

.. autoclass:: uplink.converters.MarshmallowConverter

.. note::

    Starting with version v0.5, this converter factory is automatically
    included if you have :py:mod:`marshmallow` installed, so you don't need
    to provide it when constructing your consumer instances.

Pydantic
===========

.. versionadded:: v0.9.2

Uplink comes with optional support for :py:mod:`pydantic`.

.. autoclass:: uplink.converters.PydanticConverter

.. note::

    Starting with version v0.9.2, this converter factory is automatically
    included if you have :py:mod:`pydantic` installed, so you don't need
    to provide it when constructing your consumer instances.

.. _`converting lists and mappings`:

Converting Collections
======================

.. versionadded:: v0.5.0

Uplink can convert collections of a type, such as deserializing a
response body into a list of users. If you have :py:mod:`typing`
installed (the module is part of the standard library starting Python
3.5), you can use type hints (see :pep:`484`) to specify such
conversions. You can also leverage this feature without :py:mod:`typing`
by using one of the proxy types defined in :py:class:`uplink.types`.

The following converter factory implements this feature and is automatically
included, so you don't need to provide it when constructing your consumer
instance:

.. autoclass:: uplink.converters.TypingConverter

Here are the collection types defined in :py:class:`uplink.types`. You can
use these or the corresponding type hints from :py:class:`typing` to leverage
this feature:

.. TODO: using autoclass:: uplink.types doesn't work when deployed to
         uplink.readthedocs.io for some reason. Figure out why!

.. autodata:: uplink.types.List
    :annotation:

    A proxy for :py:class:`typing.List` that is safe to use in type
    hints with Python 3.4 and below.

    .. code-block:: python

        @returns.from_json
        @get("/users")
        def get_users(self) -> types.List[str]:
            """Fetches all users"""

.. autodata:: uplink.types.Dict
    :annotation:

    A proxy for :py:class:`typing.Dict` that is safe to use in type
    hints with Python 3.4 and below.

    .. code-block:: python

        @returns.from_json
        @get("/users")
        def get_users(self) -> types.Dict[str, str]:
            """Fetches all users"""

Writing Custom JSON Converters
==============================

As a shorthand, you can define custom JSON converters using the
:py:class:`@loads.from_json <uplink.loads.from_json>` (deserialization) and
:py:class:`@dumps.to_json <uplink.dumps.to_json>` (serialization) decorators.

These classes can be used as decorators to create converters of a class
and its subclasses:

.. code-block:: python

    # Creates a converter that can deserialize the given `json` in to an
    # instance of a `Model` subtype.
    @loads.from_json(Model)
    def load_model_from_json(model_type, json):
        ...

.. note::

    Unlike consumer methods, these functions should be defined outside
    of a class scope.

To use the converter, provide the generated converter object when
instantiating a :py:class:`~uplink.Consumer` subclass, through the
:py:attr:`converter` constructor parameter:

.. code-block:: python

    github = GitHub(BASE_URL, converter=load_model_from_json)

Alternatively, you can add the :py:func:`@install <uplink.install>` decorator to
register the converter function as a default converter, meaning the
converter will be included automatically with any consumer instance and
doesn't need to be explicitly provided through the :py:obj:``converter``
parameter:

.. code-block:: python

    from uplink import install, loads

    # Register the function as a default loader for the given model class.
    @install
    @loads.from_json(Model)
    def load_model_from_json(model_type, json):
        ...

.. autoclass:: uplink.loads
    :members:

.. autoclass:: uplink.dumps
    :members:
