Authentication
==============

This section covers how to do authentication with Uplink.

Basic Authentication
--------------------

In v0.4, we added the :py:attr:`auth` parameter to the
:py:class:`uplink.Consumer` constructor.

Now it's simple to construct a consumer that uses HTTP Basic
Authentication with all requests:

.. code-block:: python

    github = GitHub(BASE_URL, auth=("user", "pass"))

Other Authentication
--------------------

Often, APIs accept credentials as header values (e.g., Bearer tokens) or
query parameters. Your request method can handle these types of
authentication by simply accepting the user's credentials as an
argument:

.. code-block:: python

    @post("/user")
    def update_user(self, access_token: Query, **info: Body):
        """Update the user associated to the given access token."""

If several request methods require authentication, you can persist the token
through the consumer's :obj:`session <uplink.Consumer.session>` property:

.. code-block:: python

    class GitHub(Consumer):

        def __init__(self, access_token):
            self.session.params["access_token"] = access_token
            ...


Using Auth Support for Requests and aiohttp
-------------------------------------------

As we work towards Uplink's v1.0 release, improving built-in support for other
types of authentication is a continuing goal.

With that said, if Uplink currently doesn't offer a solution for you
authentication needs, you can always leverage the available auth support for
the underlying HTTP client.

For instance, :py:mod:`requests` offers out-of-the-box support for
making requests with HTTP Digest Authentication, which you can leverage
like so:

.. code-block:: python

    from requests.auth import HTTPDigestAuth

    client = uplink.RequestsClient(cred=HTTPDigestAuth("user", "pass"))
    api = MyApi(BASE_URL, client=client)

You can also use other third-party libraries that extend auth support
for the underlying client. For instance, you can use `requests-oauthlib
<https://github.com/requests/requests-oauthlib>`_ for doing OAuth with
Requests:

.. code-block:: python

    from requests_oauthlib import OAuth2Session

    session = OAuth2Session(...)
    api = MyApi(BASE_URL, client=session)
