.. _serialization:

Serialization
*************

Using Marshmallow Schemas
=========================

Uplink supports converting objects to and from HTTP requests and
responses, using :class:`marshmallow`.

(De)serialization of Custom Objects
===================================

Uplink makes it easy to convert an HTTP response body into a custom
Python object, whether you leverage Uplink's built-in support for
libraries such as :py:mod:`marshmallow` or use :py:class:`uplink.loads`
to write custom conversion logic that fits your unique needs.

At the least, you need to specify the expected return type using a
decorator from the :py:class:`uplink.returns` module. For example,
:py:class:`uplink.returns.from_json` is handy when working with APIs that
provide JSON responses:

.. code-block:: python

    @returns.from_json(User)
    @get("users/{username}")
    def get_user(self, username): pass

Python 3 users can alternatively use a return type hint:

.. code-block:: python

    @returns.from_json
    @get("users/{username}")
    def get_user(self, username) -> User: pass

Next, if your objects (e.g., :py:obj:`User`) are not defined
using a library for whom Uplink has built-in support (such as
:py:mod:`marshmallow`), you will also need to register a strategy that
tells Uplink how to convert the HTTP response into your expected return
type.

To this end, the :py:class:`uplink.loads` class has various methods for
defining deserialization strategies for different formats. For the above
example, we can use :py:meth:`uplink.loads.from_json`:

.. code-block:: python

    @loads.from_json(User)
    def user_loader(user_cls, json):
        return user_cls(json["id"], json["username"])

The decorated function, :py:func:`user_loader`, can then be passed into the
:py:attr:`converter` constructor parameter when instantiating a
:py:class:`uplink.Consumer` subclass:

.. code-block:: python

    my_client = MyConsumer(base_url=..., converter=user_loader)

Alternatively, you can add the :py:meth:`uplink.loads.install` decorator to
register the converter function as a default converter, meaning the converter
will be included automatically with any consumer instance and doesn't need to
be explicitly provided through the :py:obj:`converter` parameter:

.. code-block:: python
   :emphasize-lines: 1

    @loads.install
    @loads.from_json(User)
    def user_loader(user_cls, json):
        return user_cls(json["id"], json["username"])

.. note::

    For API endpoints that return collections (such as a list of
    :py:obj:`User`), Uplink offers built-in support for :ref:`converting
    lists and mappings`: simply define a deserialization strategy for
    the element type (e.g., :py:obj:`User`), and Uplink handles the
    rest!

Converting Collections
======================




Other Serialization Formats (e.g., Protocol Buffers)
====================================================
