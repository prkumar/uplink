.. Uplink documentation master file, created by
   sphinx-quickstart on Sun Sep 24 19:40:30 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Uplink 📡
*********
A Declarative HTTP Client for Python. Inspired by `Retrofit
<http://square.github.io/retrofit/>`__.

|Release| |Python Version| |License| |Coverage Status|

.. note::

   Uplink is currently in initial development and, therefore, not
   production ready at the moment. Furthermore, as the package follows a
   `semantic versioning <https://packaging.python.org/tutorials/distributing-packages/#semantic-versioning-preferred>`__
   scheme, the public API outlined in this documentation should be
   considered tentative until the :code:`v1.0.0` release.

   However, while Uplink is under construction, we invite eager users
   to install early and provide open feedback, which can be as simple as
   opening a GitHub issue when you notice a missing feature, latent defect,
   documentation oversight, etc.

   Moreover, for those interested in contributing, checkout the `Contribution
   Guide on GitHub`_ ('tis `Hacktoberfest`_, after all)!

.. _`Contribution Guide on GitHub`: https://github.com/prkumar/uplink/blob/master/CONTRIBUTING.rst
.. _Hacktoberfest: https://hacktoberfest.digitalocean.com/

A Quick Walkthrough, with GitHub API v3:
========================================
Using decorators and function annotations, turn your Python class into a
self-describing consumer of your favorite HTTP webservice:

.. code-block:: python

    from uplink import *

    @headers({"Accept": "application/vnd.github.v3.full+json"})
    class GitHub(Consumer):

        @get("/users/{username}")
        def get_user(self, username):
            """Get a single user."""

        @json
        @patch("/user")
        def update_user(self, access_token: Query, **info: Body):
            """Update an authenticated user."""

To construct a consumer object, simply instantiate the
:py:class:`uplink.Consumer` subclass:

.. code-block:: python

    github = GitHub(base_url="https://api.github.com/")

To access the GitHub API with this instance, we can invoke any of the
methods that we defined in our class definition above. To illustrate,
let's update my GitHub profile bio with :py:meth:`update_user`:

.. code-block:: python

    response = github.update_user(token, bio="Beam me up, Scotty!")

*Voila*, the method seamlessly builds the request (using the decorators
and annotations from the method's definition) and executes it in the same call!

By default, Uplink uses the powerful `Requests
<http://docs.python-requests.org/en/master/>`_ library.
So, the :py:obj:`response` returned above is simply a
:py:class:`requests.Response` (`documentation
<http://docs.python-requests.org/en/master/api/#requests.Response>`__):

.. code-block:: python

    print(response.json()) # {u'disk_usage': 216141, u'private_gists': 0, ...

In essence, Uplink delivers reusable and self-sufficient objects for
accessing HTTP webservices, with minimal code and user pain ☺️ .


Asynchronous Requests
---------------------
Uplink includes support for non-blocking requests with asyncio (for Python 3.4+)
and Twisted (for all supported Python versions). For example, let's use our
consumer to fetch GitHub users concurrently given their :py:obj:`usernames`:

.. code-block:: python
   :emphasize-lines: 1,2

   # Create a consumer that returns awaitable responses
   github = GitHub("https://api.github.com/", client=clients.Aiohttp)

   # Fetch the users concurrently:
   futures = map(github.get_user, usernames)
   loop = asyncio.get_event_loop()
   print(loop.run_until_complete(asyncio.gather(*futures)))

To learn more about Uplink's support for concurrent requests, see
:ref:`non-blocking requests`. Also, `this Gist
<https://gist.github.com/prkumar/4e905edb988bc3d3d95e680ef043f934>`_
provides short examples for using Uplink with asyncio and Twisted.


The User Manual
===============

Follow this guide to get up and running with Uplink.

.. toctree::
   :maxdepth: 2

   install.rst
   introduction.rst
   getting_started.rst
   advanced.rst

..
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
.. |License| image:: https://img.shields.io/github/license/prkumar/uplink.svg
   :target: https://github.com/prkumar/uplink/blob/master/LICENSE
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/uplink.svg
   :target: https://pypi.python.org/pypi/uplink
.. |Release| image:: https://img.shields.io/github/release/prkumar/uplink/all.svg
   :target: https://github.com/prkumar/uplink
