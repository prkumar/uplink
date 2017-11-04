Uplink
******
|PyPI Version| |Build Status| |Coverage Status| |Documentation Status|

- Builds Reusable Objects for Consuming Web APIs.
- Works with Requests, asyncio, and Twisted.
- Inspired by `Retrofit <http://square.github io/retrofit/>`__.

A Quick Walkthrough, with GitHub API v3
=======================================
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
GitHub Enterprise instance by simply changing the ``base_url``.):

.. code-block:: python

    github = GitHub(base_url="https://api.github.com/")

To access the GitHub API with this instance, we can invoke any of the
methods that we defined in our class definition above. To illustrate,
let's update my GitHub profile bio with ``update_user``:

.. code-block:: python

    response = github.update_user(oauth_token, bio="Beam me up, Scotty!")

*Voila*, the method seamlessly builds the request (using the decorators
and annotations from the method's definition) and executes it in the same call.
And, by default, Uplink uses the powerful `Requests
<http://docs.python-requests.org/en/master/>`_ library. So, the
returned ``response`` is simply a ``requests.Response`` (`documentation
<http://docs.python-requests.org/en/master/api/#requests.Response>`__):

.. code-block:: python

    print(response.json()) # {u'disk_usage': 216141, u'private_gists': 0, ...

In essence, Uplink delivers reusable and self-sufficient objects for
accessing HTTP webservices, with minimal code and user pain ☺️.

Asynchronous Requests
---------------------
Uplink includes support for concurrent requests with asyncio (for Python 3.4+)
and Twisted (for all supported Python versions).

For example, let's create an instance of our GitHub API consumer that
returns awaitable responses using ``aiohttp``:

.. code-block:: python

   github = GitHub("https://api.github.com/", client=uplink.AiohttpClient())

Then, given a list of GitHub ``usernames``, we can use the ``get_user`` method
to fetch users concurrently with an ``asyncio`` event loop:

.. code-block:: python

   futures = map(github.get_user, usernames)
   loop = asyncio.get_event_loop()
   print(loop.run_until_complete(asyncio.gather(*futures)))

To learn more about Uplink's support for asynchronous requests, checkout
the `documentation
<http://uplink.readthedocs.io/en/latest/advanced.html#making-non-blocking-requests>`_.
Also, `this Gist
<https://gist.github.com/prkumar/4e905edb988bc3d3d95e680ef043f934>`_
provides short examples for using Uplink with asyncio and Twisted.

Installation
============
``uplink`` supports Python 2.7 & 3.3-3.7.

To install the latest stable release, you can use ``pip``:

::

    $ pip install uplink


If you are interested in the cutting-edge, preview the upcoming release with:

::

   $ pip install https://github.com/prkumar/uplink/archive/master.zip

Documentation
=============
For more details, check out the documentation at http://uplink.readthedocs.io/.

Contributing
============
Want to report a bug, request a feature, or contribute code to Uplink?
Checkout the `Contribution Guide <CONTRIBUTING.rst>`_ for where to start.
Thank you for taking the time to improve an open source project 💜

.. |Build Status| image:: https://travis-ci.org/prkumar/uplink.svg?branch=master
   :target: https://travis-ci.org/prkumar/uplink
.. |Coverage Status| image:: https://coveralls.io/repos/github/prkumar/uplink/badge.svg?branch=master
   :target: https://coveralls.io/github/prkumar/uplink?branch=master
.. |Documentation Status| image:: https://readthedocs.org/projects/uplink/badge/?version=latest
   :target: http://uplink.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
.. |License| image:: https://img.shields.io/github/license/prkumar/uplink.svg
   :target: https://github.com/prkumar/uplink/blob/master/LICENSE
.. |PyPI Version| image:: https://img.shields.io/pypi/v/uplink.svg
   :target: https://pypi.python.org/pypi/uplink
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/uplink.svg
   :target: https://pypi.python.org/pypi/uplink
