.. Uplink documentation master file, created by
   sphinx-quickstart on Sun Sep 24 19:40:30 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Uplink 📡
*********
A Declarative HTTP Client for Python. Inspired by `Retrofit
<http://square.github.io/retrofit/>`__.

|Release| |Python Version| |License| |Coverage Status| |GitHub Discussions|

.. _`Contribution Guide on GitHub`: https://github.com/prkumar/uplink/blob/master/CONTRIBUTING.md
.. _Hacktoberfest: https://hacktoberfest.digitalocean.com/

.. note::

   Uplink is in beta development. The public API is still evolving,
   but we expect most changes to be backwards compatible at this point.

Uplink turns your HTTP API into a Python class.

.. code-block:: python

   from uplink import Consumer, get, Path, Query


   class GitHub(Consumer):
       """A Python Client for the GitHub API."""

       @get("users/{user}/repos")
       def get_repos(self, user: Path, sort_by: Query("sort")):
          """Get user's public repositories."""

Build an instance to interact with the webservice.

.. code-block:: python

   github = GitHub(base_url="https://api.github.com/")

Then, executing an HTTP request is as simply as invoking a method.

.. code-block:: python

   repos = github.get_repos(user="octocat", sort_by="created")

The returned object is a friendly :py:class:`requests.Response`:

.. code-block:: python

   print(repos.json())
   # Output: [{'id': 64778136, 'name': 'linguist', ...

For sending non-blocking requests, Uplink comes with support for
:py:mod:`aiohttp` and :py:mod:`twisted` (`example
<https://github.com/prkumar/uplink/tree/master/examples/async-requests>`_).

Features
========

- **Quickly Define Structured API Clients**

  - Use decorators and type hints to describe each HTTP request
  - JSON, URL-encoded, and multipart request body and file upload
  - URL parameter replacement, request headers, and query parameter support

- **Bring Your Own HTTP Library**

  - `Non-blocking I/O support`_ for Aiohttp and Twisted
  - :ref:`Supply your own session <swap_default_http_client>` (e.g., :class:`requests.Session`) for greater control

- **Easy and Transparent Deserialization/Serialization**

  - Define :ref:`custom converters <custom_json_deserialization>` for your own objects
  - Support for |marshmallow|_ schemas and :ref:`handling collections <converting_collections>` (e.g., list of Users)
  - Support for pydantic models and :ref:`handling collections <converting_collections>` (e.g., list of Repos)

- **Extendable**

  - Install optional plugins for additional features (e.g., `protobuf support`_)
  - Compose :ref:`custom response and error handling <custom response handler>` functions as middleware

- **Authentication**

  - Built-in support for :ref:`Basic Authentication <basic_authentication>`
  - Use existing auth libraries for supported clients (e.g., |requests-oauthlib|_)

Uplink officially supports Python 2.7 & 3.5+.

.. note::

   Python 2.7 suport will be removed in v0.10.0.

.. |marshmallow| replace:: ``marshmallow``
.. |requests-oauthlib| replace:: ``requests-oauthlib``
   
.. _`Non-blocking I/O support`: https://github.com/prkumar/uplink/tree/master/examples/async-requests
.. _`marshmallow`: https://github.com/prkumar/uplink/tree/master/examples/marshmallow
.. _`custom response and error handling`: https://uplink.readthedocs.io/en/latest/user/quickstart.html#response-and-error-handling
.. _`protobuf support`: https://github.com/prkumar/uplink-protobuf
.. _`requests-oauthlib`: https://github.com/requests/requests-oauthlib

User Testimonials
=================

**Michael Kennedy** (`@mkennedy`_), host of `Talk Python`_ and `Python Bytes`_ podcasts-

   Of course our first reaction when consuming HTTP resources in Python is to
   reach for Requests. But for *structured* APIs, we often want more than ad-hoc
   calls to Requests. We want a client-side API for our apps. Uplink is
   the quickest and simplest way to build just that client-side API.
   Highly recommended.

.. _@mkennedy: https://twitter.com/mkennedy
.. _`Talk Python`: https://twitter.com/TalkPython
.. _`Python Bytes`: https://twitter.com/pythonbytes

**Or Carmi** (`@liiight`_), notifiers_ maintainer-

    Uplink's intelligent usage of decorators and typing leverages the most
    pythonic features in an elegant and dynamic way. If you need to create an
    API abstraction layer, there is really no reason to look elsewhere.

.. _@liiight: https://github.com/liiight
.. _notifiers: https://github.com/notifiers/notifiers


User Manual
===========

Follow this guide to get up and running with Uplink.

.. toctree::
   :maxdepth: 2

   user/install.rst
   user/quickstart.rst
   user/auth.rst
   user/serialization.rst
   user/clients.rst
   user/tips.rst

API Reference
=============

This guide details the classes and methods in Uplink's public API.

.. toctree::
   :maxdepth: 3

   dev/index

Miscellaneous
=============

.. toctree::
   :maxdepth: 2

   changes.rst


.. |GitHub Discussions| image:: https://img.shields.io/github/discussions/prkumar/uplink.png
   :target: https://github.com/prkumar/uplink/discussions
.. |Coverage Status| image:: https://img.shields.io/codecov/c/github/prkumar/uplink.svg
   :alt: Codecov
   :target: https://codecov.io/gh/prkumar/uplink
.. |License| image:: https://img.shields.io/github/license/prkumar/uplink.svg
   :target: https://github.com/prkumar/uplink/blob/master/LICENSE
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/uplink.svg
   :target: https://pypi.python.org/pypi/uplink
.. |Release| image:: https://img.shields.io/github/release/prkumar/uplink/all.svg
   :target: https://github.com/prkumar/uplink
