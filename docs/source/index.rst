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

   Uplink is currently in initial development. Until the official
   release (``v1.0.0``), the public API should be considered provisional.
   Although we don't expect any considerable changes to the API at this point,
   please avoid using the code in production, for now.

   However, while Uplink is under construction, we invite eager users to
   install early and provide open feedback, which can be as simple as
   opening a GitHub issue when you notice a missing feature, latent
   defect, documentation oversight, etc.

   Moreover, for those interested in contributing, checkout the `Contribution
   Guide on GitHub`_!

.. _`Contribution Guide on GitHub`: https://github.com/prkumar/uplink/blob/master/CONTRIBUTING.rst
.. _Hacktoberfest: https://hacktoberfest.digitalocean.com/

Uplink turns your HTTP API into a Python class.

.. code-block:: python

   from uplink import Consumer, get, headers, Path, Query

   class GitHub(Consumer):

      @get("users/{user}/repos")
      def list_repos(self, user: Path, sort_by: Query("sort")):
         """Get user's public repositories."""

Build an instance to interact with the webservice.

.. code-block:: python

   github = GitHub(base_url="https://api.github.com/")

Then, executing an HTTP request is as simply as invoking a method.

.. code-block:: python

   repos = github.list_repos("octocat", sort_by="created")

The returned object is a friendly :py:class:`requests.Response`:

.. code-block:: python

   print(repos.json())
   # Output: [{'id': 64778136, 'name': 'linguist', ...

For sending non-blocking requests, Uplink comes with support for
:py:mod:`aiohttp` and :py:mod:`twisted` (`example
<https://github.com/prkumar/uplink/tree/master/examples/async-requests>`_).

Use decorators and function annotations to describe the HTTP request:

* URL parameter replacement and query parameter support
* Convert responses into Python objects (e.g., using :py:mod:`marshmallow`)
* JSON, URL-encoded, and multipart request body and file upload
* Inject functions as **middleware** to define custom response and error handling


The User Manual
===============

Follow this guide to get up and running with Uplink.

.. toctree::
   :maxdepth: 2

   install.rst
   introduction.rst
   quickstart.rst
   auth.rst
   tips.rst

The Public API
==============

This guide details the classes and methods in Uplink's public API.

.. toctree::
   :maxdepth: 2

   decorators.rst
   types.rst
   clients.rst
   converters.rst
   changes.rst


.. |Coverage Status| image:: https://img.shields.io/codecov/c/github/prkumar/uplink.svg
   :alt: Codecov
   :target: https://codecov.io/gh/prkumar/uplink
.. |Gitter| image:: https://badges.gitter.im/python-uplink/Lobby.svg
   :target: https://gitter.im/python-uplink/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
   :alt: Join the chat at https://gitter.im/python-uplink/Lobby
.. |License| image:: https://img.shields.io/github/license/prkumar/uplink.svg
   :target: https://github.com/prkumar/uplink/blob/master/LICENSE
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/uplink.svg
   :target: https://pypi.python.org/pypi/uplink
.. |Release| image:: https://img.shields.io/github/release/prkumar/uplink/all.svg
   :target: https://github.com/prkumar/uplink
