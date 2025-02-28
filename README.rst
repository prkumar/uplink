Uplink
******
|PyPI Version| |Build Status| |Coverage Status| |Code Climate| |Documentation Status|
|GitHub Discussions| |Gitter| |Code Style|

- Builds Reusable Objects for Consuming Web APIs.
- Works with **Requests**, **aiohttp**, and **Twisted**.
- Inspired by `Retrofit <http://square.github.io/retrofit/>`__.

A Quick Walkthrough, with GitHub API v3
=======================================
Uplink turns your HTTP API into a Python class.

.. code-block:: python

   from uplink import Consumer, get, Path, Query


   class GitHub(Consumer):
       """A Python Client for the GitHub API."""

       @get("users/{user}/repos")
       def get_repos(self, user: Path, sort_by: Query("sort")):
           """Retrieves the user's public repositories."""

Build an instance to interact with the webservice.

.. code-block:: python

   github = GitHub(base_url="https://api.github.com/")

Then, executing an HTTP request is as simply as invoking a method.

.. code-block:: python

   repos = github.get_repos(user="octocat", sort_by="created")

The returned object is a friendly |requests.Response|_:

.. |requests.Response| replace:: ``requests.Response``
.. _requests.Response: http://docs.python-requests.org/en/master/api/#requests.Response

.. code-block:: python

   print(repos.json())
   # Output: [{'id': 64778136, 'name': 'linguist', ...

For sending non-blocking requests, Uplink comes with support for
|aiohttp and twisted|_.

.. |aiohttp and twisted| replace:: ``aiohttp`` and ``twisted``
.. _`aiohttp and twisted`: https://github.com/prkumar/uplink/tree/master/examples/async-requests

Ready to launch your first API client with Uplink? Start with this `quick tutorial`_!

Features
========

- **Quickly Define Structured API Clients**

  - Use decorators and type hints to describe each HTTP request
  - JSON, URL-encoded, and multipart request body and file upload
  - URL parameter replacement, request headers, and query parameter support

- **Bring Your Own HTTP Library**

  - `Non-blocking I/O support`_ for Aiohttp and Twisted
  - `Supply your own session`_ (e.g., ``requests.Session``) for greater control

- **Easy and Transparent Deserialization/Serialization**

  - Define `custom converters`_ for your own objects
  - Support for |marshmallow|_ schemas, |pydantic|_ models, and `handling collections`_ (e.g., list of Users)

- **Extendable**

  - Install optional plugins for additional features (e.g., `protobuf support`_)
  - Compose `custom response and error handling`_ functions as middleware

- **Authentication**

  - Built-in support for `Basic Authentication`_
  - Use existing auth libraries for supported clients (e.g., |requests-oauthlib|_)

Uplink officially supports Python 2.7 and 3.5+.

**Note:** Python 2.7 support will be removed in v0.10.0.

.. |marshmallow| replace:: ``marshmallow``
.. |pydantic| replace:: ``pydantic``
.. |requests-oauthlib| replace:: ``requests-oauthlib``
.. _`Non-blocking I/O support`: https://github.com/prkumar/uplink/tree/master/examples/async-requests
.. _`Supply your own session`: https://uplink.readthedocs.io/en/latest/user/clients.html#swapping-out-the-default-http-session
.. _`marshmallow`: https://github.com/prkumar/uplink/tree/master/examples/marshmallow
.. _`custom converters`: https://uplink.readthedocs.io/en/latest/user/serialization.html#custom-json-deserialization
.. _`handling collections`: https://uplink.readthedocs.io/en/latest/user/serialization.html#converting-collections
.. _`custom response and error handling`: https://uplink.readthedocs.io/en/latest/user/quickstart.html#response-and-error-handling
.. _`protobuf support`: https://github.com/prkumar/uplink-protobuf
.. _`requests-oauthlib`: https://github.com/requests/requests-oauthlib
.. _`Basic Authentication`: https://uplink.readthedocs.io/en/latest/user/auth.html#basic-authentication
.. _`pydantic`: https://pydantic-docs.helpmanual.io/

Installation
============

To install the latest stable release, you can use ``pip`` (or ``pipenv``):

::

    $ pip install -U uplink

If you are interested in the cutting-edge, preview the upcoming release with:

::

   $ pip install https://github.com/prkumar/uplink/archive/master.zip

Extra! Extra!
-------------

Further, uplink has optional integrations and features. You can view a full list
of available extras `here <https://uplink.readthedocs.io/en/latest/user/install.html#extras>`_.

When installing Uplink with ``pip``, you can select extras using the format:

::

   $ pip install -U uplink[extra1, extra2, ..., extraN]


For instance, to install ``aiohttp`` and ``marshmallow`` support:

::

   $ pip install -U uplink[aiohttp, marshmallow]


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


Documentation
=============

Check out the library's documentation at https://uplink.readthedocs.io/.

For new users, a good place to start is this `quick tutorial`_.


Community
=========

Use the `Discussions`_ tab on GitHub to join the conversation! Ask questions, provide feedback,
and meet other users!

We're migrating our community from `Gitter`_ to GitHub `Discussions`_. Feel free to search our
Gitter lobby for past questions and answers. However, to help us transition, please start new
threads/posts in GitHub Discussions instead of Gitter.

.. _Discussions: https://github.com/prkumar/uplink/discussions
.. _Gitter: https://gitter.im/python-uplink/Lobby


Contributing
============

Want to report a bug, request a feature, or contribute code to Uplink?
Checkout the `Contribution Guide`_ for where to start.
Thank you for taking the time to improve an open source project :purple_heart:

.. |GitHub Discussions| image:: https://img.shields.io/github/discussions/prkumar/uplink.png
   :target: https://github.com/prkumar/uplink/discussions
.. |Build Status| image:: https://travis-ci.com/prkumar/uplink.svg?branch=master
   :target: https://travis-ci.com/prkumar/uplink
.. |Code Climate| image:: https://api.codeclimate.com/v1/badges/d5c5666134763ff1d6c0/maintainability
   :target: https://codeclimate.com/github/prkumar/uplink/maintainability
   :alt: Maintainability
.. |Code Style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black
   :alt: Code style: black
.. |Coverage Status| image:: https://img.shields.io/codecov/c/github/prkumar/uplink.svg
   :alt: Codecov
   :target: https://codecov.io/gh/prkumar/uplink
.. |Documentation Status| image:: https://readthedocs.org/projects/uplink/badge/?version=latest
   :target: http://uplink.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
.. |Gitter| image:: https://badges.gitter.im/python-uplink/Lobby.svg
   :target: https://gitter.im/python-uplink/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
   :alt: Join the chat at https://gitter.im/python-uplink/Lobby
.. |License| image:: https://img.shields.io/github/license/prkumar/uplink.svg
   :target: https://github.com/prkumar/uplink/blob/master/LICENSE
.. |PyPI Version| image:: https://img.shields.io/pypi/v/uplink.svg
   :target: https://pypi.python.org/pypi/uplink

.. _`Contribution Guide`: https://github.com/prkumar/uplink/blob/master/CONTRIBUTING.rst
.. _`quick tutorial`: https://uplink.readthedocs.io/en/latest/user/quickstart.html
