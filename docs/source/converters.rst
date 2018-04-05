Converters
**********

The ``converter`` parameter of the :py:class:`uplink.Consumer` constructor
accepts a custom adapter class that handles serialization of HTTP
request properties and deserialization of HTTP response objects:

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

.. _`converting lists and mappings`:

Type Hints
==========

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

.. autoclass:: uplink.types

Writing a Custom Converter
==========================

You can define custom converters by using :py:class:`uplink.loads` and
:py:class:`uplink.dumps`.

These classes can be used one of two ways. First is as function
decorators:

.. code-block:: python

    # Registers the function as a loader for the given model class.
    @loads.from_json(Model)
    def load_model_from_json(model_type, json):
        ...

With this usage, the decorated function is registered as a default
converter (specifically for the class :py:class:`Model` and its
subclasses).

The alternative usage is to build a converter instance:

.. code-block:: python

    def load_model_from_json(model_type, json):
        ...

    # Creates a converter using the given loader function.
    converter = loads.from_json(Model).using(load_model_from_json)

Unlike the decorator usage, this approach does not register the function
as a default converter, meaning, to use the converter, you must supply
the generated converter object when instantiating a
:py:class:`~uplink.Consumer` subclass, through the :py:attr:`converter`
constructor parameter.

Notably, invoking the :py:meth:`~uplink.loads.by_default` method
registers the generated converter object as a default converter,
achieving parity between the two usages. Hence, the follow snippet is
equivalent to the first example using the decorator approach:

.. code-block:: python

    # Registers the function as a loader for the given model class.
    loads.from_json(Model).using(load_model_from_json).by_default()

.. autoclass:: uplink.loads

.. autoclass:: uplink.dumps