Uplink
======
Python HTTP Made Expressive. Inspired by `Retrofit <http://square.github
.io/retrofit/>`__.

|PyPI Version| |Build Status| |Coverage Status| |Documentation Status|

A Quick Walkthrough, with GitHub API v3
---------------------------------------

Using decorators and function annotations, you can turn any plain old Python
class into a self-describing consumer of your favorite HTTP webservice:


.. code-block:: python

    from uplink import *

    # To register entities that are common to all API requests, you can
    # decorate the enclosing class rather than each method separately:
    @headers({"Accept": "application/vnd.github.v3.full+json"})
    class GitHub(object):

        @get("/users/{username}")
        def get_user(self, username):
            """Get a single user."""

        @json
        @patch("/user")
        def update_user(self, access_token: Query, **info: Body):
            """Update an authenticated user."""

To construct a consumer instance, use the helper function ``uplink.build``:

.. code-block:: python

    github = build(GitHub, base_url="https://api.github.com/")

To access the GitHub API with this instance, we simply invoke any of the methods
that we defined in the interface above. To illustrate, let's update my GitHub
profile bio:

.. code-block:: python

    response = github.update_user(oauth_token, bio="Beam me up, Scotty!").execute()

*Voila*, ``update_user(...)`` seamlessly builds the request (using the
decorators and annotations from the method's definition), and ``execute()``
sends that synchronously over the network. Furthermore, the returned
``response`` is a ``requests.Response`` (`documentation
<http://docs.python-requests.org/en/master/api/#requests.Response>`__):

.. code-block:: python

    print(response.json()) # {u'disk_usage': 216141, u'private_gists': 0, ...

In essence, Uplink delivers reusable and self-sufficient objects for
accessing HTTP webservices, with minimal code and user pain ☺️.

Installation
------------

``uplink`` supports Python 2.7 & 3.3-3.7.

To install the latest stable release, you can use ``pip``:

::

    $ pip install uplink


Interested in the cutting-edge? You can install the work-in-progress for the
upcoming release with:

::

   $ pip install https://github.com/prkumar/uplink/archive/develop.zip

Documentation
-------------

For more details, check out the documentation at http://uplink.readthedocs.io/.

Contributing
------------

Looking to report a bug, request a feature, or contribute code to Uplink?
Checkout the `Contribution Guide <CONTRIBUTING.rst>`_ ! Thanks for taking
the time to improve an open source project!

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
