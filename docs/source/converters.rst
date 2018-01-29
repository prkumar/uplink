Converters
**********

The ``converter`` parameter of the :py:class:`uplink.Consumer` constructor
accepts an adapter class that handles deserialization of HTTP response objects:

.. code-block:: python

    github = GitHub(BASE_URL, converter=...)

Marshmallow
===========

.. autoclass:: uplink.MarshmallowConverter