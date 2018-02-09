Authentication
==============


Basic Authentication
--------------------

In v0.4, we added the :py:attr:`auth` parameter to the
:py:class:`uplink.Consumer` constructor.

Now, it's very simple to construct a consumer that uses HTTP Basic
Authentication with all requests:

.. code-block:: python

    github = GitHub(BASE_URL, auth=("user", "pass"))

Other Authentication
--------------------

Often, APIs accept credentials as header values or query parameters.
Your request method can handle these types of authentication by simply
accepting the user's credentials as an argument:

.. code-block:: python

    @post("/user")
    def update_user(self, access_token: Query, **info: Body):
        """Update the user associated to the given access token."""

If more than one request requires authentication, you can make the token
an argument of your consumer constructor:

.. TODO: Add link to how inject hooks into a consumer instance.

.. code-block:: python

    class GitHub(Consumer):

        def __init__(self, base_url, access_token: Query)
            ...


Using Existing Auth Support for Requests and aiohttp
----------------------------------------------------

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

.. code-block:: python:

    from requests_oauthlib import OAuth2Session

    session = OAuth2Session(...)
    api = MyApi(BASE_URL, client=session)

