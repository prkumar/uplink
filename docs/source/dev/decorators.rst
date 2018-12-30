Decorators
**********

The method decorators detailed in this section describe request properties that
are relevant to all invocations of a consumer method.

headers
=======

.. autoclass:: uplink.headers


params
======

.. autoclass:: uplink.params

json
====

.. autoclass:: uplink.json

form_url_encoded
================

.. autoclass:: uplink.form_url_encoded

multipart
=========

.. autoclass:: uplink.multipart

timeout
=======

.. autoclass:: uplink.timeout

args
====

.. autoclass:: uplink.args

response_handler
================

.. autoclass:: uplink.response_handler

error_handler
=============

.. autoclass:: uplink.error_handler

inject
======

.. autoclass:: uplink.inject


returns.*
=========

Converting an HTTP response body into a custom Python object is
straightforward with Uplink; the :py:mod:`uplink.returns` modules
exposes optional decorators for defining the expected return type and
data serialization format for any consumer method.

.. automodule:: uplink.returns
    :members:


retry
=====

.. automodule:: uplink.retry
    :members:

retry.backoffBackoff
-------------

The :mod:`uplink.retry.backoff` module exposes various backoff strategies
that can be used with the :class:`retry <uplink.retry>` decorator's
``backoff`` argument:

.. automodule:: uplink.retry.backoff
    :members:

retry.stop
----------

The :mod:`uplink.retry.stop` module exposes breaking strategies
that can be used with the :class:`retry <uplink.retry>` decorator's
``stop`` argument:

.. automodule:: uplink.retry.stop
    :members:

ratelimit
=========

.. autoclass:: uplink.ratelimit
