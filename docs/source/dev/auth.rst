.. _auth_methods:

Auth Methods
************


The ``auth`` parameter of the :py:class:`Consumer` constructor offers a way
to define an auth method to use for all requests.

.. code-block:: python

    auth_method = SomeAuthMethod(...)
    github = GitHub(BASE_URL, auth=auth_method)


BasicAuth
=========

.. autoclass:: uplink.auth.BasicAuth

ProxyAuth
=========

.. autoclass:: uplink.auth.ProxyAuth

BearerToken
===========

.. autoclass:: uplink.auth.BearerToken

MultiAuth
=========

.. autoclass:: uplink.auth.MultiAuth

ApiTokenParam
=============

.. autoclass:: uplink.auth.ApiTokenParam

ApiTokenHeader
==============

.. autoclass:: uplink.auth.ApiTokenHeader
