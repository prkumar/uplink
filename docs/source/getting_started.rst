Getting Started
***************

Send a Request
==============

Sending a simple

Setting the URL
===============

Path Variables
==============

Implicit :code:`Path` Annotations
----------------------------------

When building the consumer instance, :py:func:`uplink.build` will try to resolve
unannotated method arguments by matching their names with URI path parameters.

For example, consider the consumer defined below, in which the method
:py:meth:`get_user` has an unannotated argument, :py:attr:`username`.
Since its name matches the URI path parameter ``{username}``,
:py:mod:`uplink` will auto-annotate the argument with :py:class:`Path`
for us:

.. code-block:: python

    class GitHubService(object):
        @uplink.get("user/{username}")
        def get_user(self, username): pass

Important to note, failure to resolve all unannotated function arguments
raises an :py:class:`~uplink.InvalidRequestDefinitionError`.

Query Parameters
================

HTTP Headers
============

URL-Encoded Request Body
========================

Send Multipart Form Data
========================

JSON Requests, and Other Content Types
======================================







