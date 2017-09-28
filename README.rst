Uplink
======

A Declarative HTTP Client for Python, inspired by `Retrofit
<http://square.github.io/retrofit/>`__.

|Build Status| |Coverage Status| |Documentation Status|

Build your API using decorators (and function annotations in Python 3):

.. code:: python

    from uplink import *


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

Then, ``uplink`` handles the rest:

.. code:: python

    github = build(GitHubService, base_url="https://api.github.com/")
    response = github.update_user(oauth_token, bio="Scotty, beam me up.").execute()

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
