Function Annotations
********************

For programming in general, function parameters drive a function's
dynamic behavior; a function's output depends normally on its inputs.
With :py:mod:`uplink`, function arguments parametrize an HTTP request,
and you indicate the dynamic parts of the request by appropriately
annotating those arguments with the classes detailed in this section.

Path
====

.. autoclass:: uplink.Path

Query
=====

.. autoclass:: uplink.Query
   :members: with_value

QueryMap
========

.. autoclass:: uplink.QueryMap
   :members: with_value

Header
======

.. autoclass:: uplink.Header
   :members: with_value

HeaderMap
=========

.. autoclass:: uplink.HeaderMap
   :members: with_value

Field
=====

.. autoclass:: uplink.Field


FieldMap
========

.. autoclass:: uplink.FieldMap

Part
====

.. autoclass:: uplink.Part

PartMap
=======

.. autoclass:: uplink.PartMap

Body
====

.. autoclass:: uplink.Body

Url
===

.. autoclass:: uplink.Url
