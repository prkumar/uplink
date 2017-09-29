Uplink
======

Python HTTP Made Expressive. Inspired by `Retrofit <http://square.github
.io/retrofit/>`__.

|PyPI Version| |Build Status| |Coverage Status| |License| |Python Version|
|Documentation Status|

----

Using decorators and function annotations, turn any plain old Python class
into a HTTP API consumer:

.. code:: python

    from uplink import *

    # To register entities that are common to all API requests, you can
    # decorate the enclosing class rather than each method separately:
    @headers({"Accept": "application/vnd.github.v3.full+json"})
    class GitHubService(object):

        @get("/users/{username}")
        def get_user(self, username):
            """Get a single user."""
            pass

        @json
        @patch("/user")
        def update_user(self, access_token: Query, **info: Body):
            """Update an authenticated user."""
            pass

To construct a consumer instance, use the helper function ``uplink.build``:

.. code:: python

    github = build(GitHubService, base_url="https://api.github.com/")
    github.update_user(oauth_token, bio="Beam me up, Scotty!").execute()

Notably, ``github.update_user(...).execute()`` returns a `requests.Response
<http://docs.python-requests.org/en/master/api/#requests.Response>`__
instance, which encapsulates the server's response to the underlying HTTP
request.

Installation
------------

``uplink`` supports Python 2.7 & 3.3-3.7. To install the package, you can use
``pip``:

::

    $ pip install uplink

Documentation
-------------

For more details, check out the documentation at http://uplink.readthedocs.io/.

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
