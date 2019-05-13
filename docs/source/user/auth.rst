Authentication
==============

This section covers how to do authentication with Uplink.

In v0.4, we added the :py:attr:`auth` parameter to the
:py:class:`uplink.Consumer` constructor which allowed for
sending HTTP Basic Authentication with all requests.

In v0.9, we added more auth methods which can be used in the
:py:attr:`auth` parameter of the :py:class:`uplink.Consumer`
constructor. If you are using an uplink-based API library,
the library might extend these methods with additional
API-specific auth methods.

Some common auth methods are described below, but for a
complete list of auth methods provided with Uplink, see
the :ref:`auth_methods` reference.

.. _basic_authentication:

Basic Authentication
--------------------

It's simple to construct a consumer that uses HTTP Basic
Authentication with all requests:

.. code-block:: python

    github = GitHub(BASE_URL, auth=("user", "pass"))

Proxy Authentication
--------------------

If you need to supply credentials for an intermediate proxy
in addition to the API's HTTP Basic Authentication, use
:py:class:`uplink.auth.MultiAuth` with :py:class:`uplink.auth.ProxyAuth`
and :py:class:`uplink.auth.BasicAuth`.

.. code-block:: python

    from uplink.auth import BasicAuth, MultiAuth, ProxyAuth

    auth_methods = MultiAuth(
        ProxyAuth("proxy_user", "proxy_pass"),
        BasicAuth("user", "pass")
    )
    github = GitHub(BASE_URL, auth=auth_methods)

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

        def __init__(self, base_url, access_token):
            super(GitHub, self).__init__(base_url=base_url)
            self.session.params["access_token"] = access_token
            ...

As of v0.9, you can also supply these tokens via the :py:attr:`auth`
parameter of the :py:class:`uplink.Consumer` constructor. This is
like adding the token to the session (above) so that the token is
sent as part of every request.

.. code-block:: python

    from uplink.auth import ApiTokenParam, ApiTokenHeader, BearerToken

    # Passing an auth token as a query parameter
    token_auth = ApiTokenParam("access_token", access_token)
    github = GitHub(BASE_URL, auth=token_auth)

    # Passing the token as a header value
    token_auth = ApiTokenHeader("Access-Token", access_token)
    github = GitHub(BASE_URL, auth=token_auth)

    # Passing a Bearer auth token
    bearer_auth = BearerToken(access_token)
    github = GitHub(BASE_URL, auth=bearer_auth)

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
