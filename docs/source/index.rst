.. Uplink documentation master file, created by
   sphinx-quickstart on Sun Sep 24 19:40:30 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Uplink 📡
==========
A Declarative HTTP Client for Python, inspired by `Retrofit
<http://square.github.io/retrofit/>`__.

|Release| |Python Version| |License| |Coverage Status|

.. note:: **Uplink** is currently in alpha development and, thus, not
    production ready at the moment. However, while the package is under
    construction, enthusiastic early adopters are more than welcome to install
    and provide feedback, as we work towards the official release. Moreover,
    for those interested in contributing, I plan to publish a contribution
    guide soon, but in the meantime, please feel free to reach out!

----

**A simple example, with GitHub API v3:**

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

To construct a consumer instance, use the helper function :py:func:`uplink.build`:

.. code:: python

    github = build(GitHubService, base_url="https://api.github.com/")
    github.update_user(oauth_token, bio="Beam me up, Scotty!").execute()

Notably, :py:meth:`github.update_user(...).execute` returns a `requests.Response
<http://docs.python-requests.org/en/master/api/#requests.Response>`__
instance, which encapsulates the server's response to the underlying HTTP
request.

.. toctree::
   :maxdepth: 2

.. |Coverage Status| image:: https://coveralls.io/repos/github/prkumar/uplink/badge.svg?branch=master
   :target: https://coveralls.io/github/prkumar/uplink?branch=master
.. |License| image:: https://img.shields.io/github/license/prkumar/uplink.svg
   :target: https://github.com/prkumar/uplink/blob/master/LICENSE
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/uplink.svg
   :target: https://pypi.python.org/pypi/uplink
.. |Release| image:: https://img.shields.io/github/release/prkumar/uplink/all.svg
   :target: https://github.com/prkumar/uplink
