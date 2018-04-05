Uplink
******
|PyPI Version| |Build Status| |Coverage Status| |Code Climate| |Documentation Status|
|Gitter|

- Builds Reusable Objects for Consuming Web APIs.
- Works with **Requests**, **asyncio**, and **Twisted**.
- Inspired by `Retrofit <http://square.github.io/retrofit/>`__.

A Quick Walkthrough, with GitHub API v3
=======================================
Uplink turns your HTTP API into a Python class.

.. code-block:: python

   from uplink import Consumer, get, headers, Path, Query

   class GitHub(Consumer):

      @get("users/{user}/repos")
      def get_repos(self, user: Path, sort_by: Query("sort")):
         """Retrieves the user's public repositories."""

Build an instance to interact with the webservice.

.. code-block:: python

   github = GitHub(base_url="https://api.github.com/")

Then, executing an HTTP request is as simply as invoking a method.

.. code-block:: python

   repos = github.get_repos("octocat", sort_by="created")

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

Use decorators and function annotations to describe the HTTP request:

* URL parameter replacement and query parameter support
* Convert response bodies into Python objects (e.g., using |marshmallow|_ or
  a `custom converter <http://uplink.readthedocs.io/en/latest/quickstart.html#deserializing-the-response-body>`_)
* JSON, URL-encoded, and multipart request body and file upload
* Inject functions as **middleware** to apply custom response and error handling

.. |marshmallow| replace:: ``marshmallow``
.. _`marshmallow`: https://github.com/prkumar/uplink/tree/master/examples/marshmallow

Installation
============
``uplink`` supports Python 2.7 & 3.3-3.7.

To install the latest stable release, you can use ``pip``:

::

    $ pip install -U uplink

If you are interested in the cutting-edge, preview the upcoming release with:

::

   $ pip install https://github.com/prkumar/uplink/archive/master.zip

Extra! Extra!
-------------

Further, uplink has optional integrations and features. You can view a full list 
of available extras `here <http://uplink.readthedocs.io/en/latest/install.html#extras>`_.

When installing Uplink with ``pip``, you can select extras using the format:

::

   $ pip install -U uplink[extra1, extra2, ..., extraN]


For instance, to install ``aiohttp`` and ``marshmallow`` support:

::

   $ pip install -U uplink[aiohttp, marshmallow]


Documentation
=============
For more details, check out the documentation at https://uplink.readthedocs.io/.

Contributing
============
Want to report a bug, request a feature, or contribute code to Uplink?
Checkout the `Contribution Guide`_ for where to start.
Thank you for taking the time to improve an open source project 💜

.. |Build Status| image:: https://travis-ci.org/prkumar/uplink.svg?branch=master
   :target: https://travis-ci.org/prkumar/uplink
.. |Code Climate| image:: https://img.shields.io/codeclimate/maintainability/prkumar/uplink.svg
   :target: https://codeclimate.com/github/prkumar/uplink/maintainability
   :alt: Maintainability
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
