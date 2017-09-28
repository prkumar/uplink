.. Uplink documentation master file, created by
   sphinx-quickstart on Sun Sep 24 19:40:30 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Uplink 📡
==========
A Declarative HTTP Client for Python, inspired by `Retrofit
<http://square.github.io/retrofit/>`__.

|Coverage Status|

Declare your API as a Python class, using decorators and function annotations
to define HTTP requests:

.. code:: python

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

Then, `uplink.build`` creates an instance:

.. code:: python

    github = build(GitHubService, base_url="https://api.github.com/")
    response = github.update_user(oauth_token, bio="Scotty, beam me up.").execute()


.. toctree::
   :maxdepth: 2

.. |Coverage Status| image:: https://coveralls.io/repos/github/prkumar/uplink/badge.svg?branch=master
   :target: https://coveralls.io/github/prkumar/uplink?branch=master