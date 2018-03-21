Converters
**********

The ``converter`` parameter of the :py:class:`uplink.Consumer` constructor
accepts an adapter class that handles serialization of HTTP
request properties and deserialization of HTTP response objects:

.. code-block:: python

    github = GitHub(BASE_URL, converter=...)


Starting with version v0.5, some out-of-the-box converters are included
automatically and don't need to be explicitly provided through the
``converter`` parameter. These implementations are detailed below.


Marshmallow
===========

Uplink comes with optional support for :py:mod:`marshmallow`. Starting with
version v0.5, this converter factory is automatically included if you have
:py:mod:`marshmallow` installed, so you don't need to provide it when
constructing your consumer instances.

.. autoclass:: uplink.converters.MarshmallowConverter


Writing a Custom Converter
==========================

.. note::

    Before writing a custom converter factory, consider instead whether
    defining a :ref:`custom response handler` could cover you use case.

You can define custom converters by extending
py:class:`uplink.converters.ConverterFactory`:

.. code-block:: python

    from uplink import converters

    class MyCustomSerializationProtocol(converters.ConverterFactory):
        ...


Here are the methods that you can override to define custom serialization or
deserialization logic:

.. autoclass:: uplink.converters.ConverterFactory


If you'd like your custom factory to be included automatically, you can
decorate your factory implementation with
:py:func:`uplink.converters.register_default_converter_factory`:

.. code-block:: python

    from uplink import converters

    @converters.register_default_converter_factory
    class MyCustomSerializationProtocol(converters.ConverterFactory):
        ...


Applying this decorator to the class avoids the need to specify the
implementation when instantiating your consumer.