.. Uplink documentation master file, created by
   sphinx-quickstart on Sun Sep 24 19:40:30 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Uplink 📡
==========
A Declarative HTTP Client for Python, inspired by `Retrofit
<http://square.github.io/retrofit/>`__.

|Release| |Python Version| |License| |Coverage Status|

.. note:: **Uplink** is currently under alpha development and, thus, very
    much under construction. Although it is not yet production ready, we
    encourage enthusiastic early adopters to install and provide feedback,
    as we work towards the official release. Moreover, if you're interested in
    becoming a contributor, please feel free to reach out.

----

*Beam me up, Scotty*: A GitHub API Example
------------------------------------------

Define your API using decorators and function annotations with plain old
Python methods:

.. code:: python

    from uplink import *

    # To register entities that are common to all API requests, you can
    # decorate the enclosing class, instead of each method separately:
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

The helper function ``uplink.build`` turns your Python class into an
expressive HTTP client:

.. code:: python

    github = build(GitHubService, base_url="https://api.github.com/")
    github.update_user(oauth_token, bio="Beam me up, Scotty!").execute()


.. toctree::
   :maxdepth: 2

.. |Coverage Status| image:: https://coveralls.io/repos/github/prkumar/uplink/badge.svg?branch=master
   :target: https://coveralls.io/github/prkumar/uplink?branch=master
.. |Release| image:: https://img.shields.io/pypi/v/uplink.svg
   :target: https://pypi.python.org/pypi/uplink
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/uplink.svg
   :target: https://pypi.python.org/pypi/uplink
.. |License| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT)