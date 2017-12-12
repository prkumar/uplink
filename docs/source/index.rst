.. Uplink documentation master file, created by
   sphinx-quickstart on Sun Sep 24 19:40:30 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Uplink 📡
*********
A Declarative HTTP Client for Python. Inspired by `Retrofit
<http://square.github.io/retrofit/>`__.

|Release| |Python Version| |License| |Coverage Status| |Gitter|

.. note::

   Uplink is currently in initial development. Up until the :code:`v1.0.0`
   release, the public API should be considered provisional, meaning that
   minor versions
   code may run in one minor version and not the other. may not be compatabl
   between minor
   versions (e.g.,
:code:`0.2
      .0` to
:code:`0.3.0`)
    may
   break compatability. Therefore, the library is not production ready at
   the moment.

   However, while Uplink is under construction, we invite eager users
   to install early and provide open feedback, which can be as simple as
   opening a GitHub issue when you notice a missing feature, latent defect,
   documentation oversight, etc.

   Moreover, for those interested in contributing, checkout the `Contribution
   Guide on GitHub`_!

.. _`Contribution Guide on GitHub`: https://github.com/prkumar/uplink/blob/master/CONTRIBUTING.rst
.. _Hacktoberfest: https://hacktoberfest.digitalocean.com/

A Quick Walkthrough, with GitHub API v3:
========================================

Uplink turns your HTTP API into a Python class. Here's how it looks like:

.. code:: python

   import uplink

   class GitHub(uplink.Consumer):
      @uplink.get("user/{user}/repos")
      def list_repos(self, user):
         """List all public repositories for the given user."""


   # Instantiate an object to interact with the webserver
   github = GitHub(base_url="https://api.github.com/"))

   # Invoke the decorated class method to execute an HTTP request.
   repos = github.list_repos("octocat")

Uplink uses the powerful `Requests
<http://docs.python-requests.org/en/master/>`_ library by default. So, the
returned list of :py:obj:`repos` is simply a :py:class:`requests.Response`:

.. code-block:: python

   >>> repos.json()
   [{'id': 18221276, 'name': 'git-consortium', ...

For sending non-blocking requests, Uplink comes with support for
:py:mod:`aiohttp` and :py:mod:`twisted`.

Uplink turns your HTTP API into a Python class.

.. code:: python

    import uplink

    class GitHub(uplink.Consumer):
        @uplink.get("users/{user}/repos")
        def list_repos(self, user):
            """Get a user's public repositories."""

Instantiate the class to begin interact with the webservice

.. code:: python

    github = GitHub(base_url="https://api.github.com/")

Then, invoke the class method to execute an HTTP request to the remote
webserver.

.. code:: python

    repos = github.list_repos("octocat")

Uplink uses the powerful `Requests
<http://docs.python-requests.org/en/master/>`_ library by default. So, the
returned list of :py:obj:`repos` is simply a :py:class:`requests.Response`:

.. code-block:: python

   print(repos.json())
   # Output: [{'id': 18221276, 'name': 'git-consortium', ...

For sending non-blocking requests, Uplink comes with support for
:py:mod:`aiohttp` and :py:mod:`twisted`.

Use decorators and function annotations to describe the HTTP request:

* URL parameter replacement and query parameter support
* Convert responses into Python objects (e.g., using :py:mod:`marshmallow`)
* JSON, URL-encoded, and multipart request body and file upload

..
   Turn a Python class into a self-describing consumer of your favorite HTTP
   webservice, using method decorators and function annotations:

   .. code-block:: python

       from uplink import *

       # To define common request metadata, you can decorate the class
       # rather than each method separately.
       @headers({"Accept": "application/vnd.github.v3.full+json"})
       class GitHub(Consumer):

           @get("/users/{username}")
           def get_user(self, username):
               """Get a single user."""

           @json
           @patch("/user")
           def update_user(self, access_token: Query, **info: Body):
               """Update an authenticated user."""

   Let's build an instance of this GitHub API consumer for the main site!
   (Notice that I can use this same consumer class to also access any
   GitHub Enterprise instance by simply changing the :py:attr:`base_url`.):

   .. code-block:: python

       github = GitHub(base_url="https://api.github.com/")

   To access the GitHub API with this instance, we can invoke any of the
   methods that we defined in our class definition above. To illustrate,
   let's update my GitHub profile bio with :py:meth:`update_user`:

   .. code-block:: python

       response = github.update_user(token, bio="Beam me up, Scotty!")

   *Voila*, the method seamlessly builds the request (using the decorators
   and annotations from the method's definition) and executes it in the same call.
   And, by default, Uplink uses the powerful `Requests
   <http://docs.python-requests.org/en/master/>`_ library. So, the returned
   :py:obj:`response` is simply a :py:class:`requests.Response`:

   .. code-block:: python

       print(response.json()) # {u'disk_usage': 216141, u'private_gists': 0, ...

   In essence, Uplink delivers reusable and self-sufficient objects for
   accessing HTTP webservices, with minimal code and user pain ☺️ .

   Asynchronous Requests
   ---------------------
   Uplink includes support for concurrent requests with asyncio (for Python 3.4+)
   and Twisted (for all supported Python versions). Checkout
   :ref:`non-blocking requests` for more.

The User Manual
===============

Follow this guide to get up and running with Uplink.

.. toctree::
   :maxdepth: 2

   install.rst
   introduction.rst
   getting_started.rst
   advanced.rst

The Public API
==============

.. todo::

   Most of this guide is unfinished and completing it is a planned
   deliverable for the ``v0.3.0`` release. At the least, this work will
   necessitate adding docstrings to the classes enumerated below.

.. toctree::
   :maxdepth: 2

   decorators.rst
   types.rst
   changes.rst


.. |Coverage Status| image:: https://coveralls.io/repos/github/prkumar/uplink/badge.svg?branch=master
   :target: https://coveralls.io/github/prkumar/uplink?branch=master
.. |Gitter| image:: https://badges.gitter.im/python-uplink/Lobby.svg
   :target: https://gitter.im/python-uplink/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
   :alt: Join the chat at https://gitter.im/python-uplink/Lobby
.. |License| image:: https://img.shields.io/github/license/prkumar/uplink.svg
   :target: https://github.com/prkumar/uplink/blob/master/LICENSE
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/uplink.svg
   :target: https://pypi.python.org/pypi/uplink
.. |Release| image:: https://img.shields.io/github/release/prkumar/uplink/all.svg
   :target: https://github.com/prkumar/uplink
