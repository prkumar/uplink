Decorators
**********

The method decorators detailed in this section describe request properties that
are relevant to all invocations of a consumer method.

headers
=======

.. autoclass:: uplink.headers

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

.. autoclass:: uplink.returns.json
