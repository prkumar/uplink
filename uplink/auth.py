"""This module implements the auth layer."""

# Standard library imports
import collections

# Third-party imports
from requests import auth

# Local imports
from uplink import utils

__all__ = [
    "ApiTokenParam",
    "ApiTokenHeader",
    "BasicAuth",
    "ProxyAuth",
    "BearerToken",
    "MultiAuth",
]


def get_auth(auth_object=None):
    if auth_object is None:
        return utils.no_op
    elif isinstance(auth_object, collections.Iterable):
        return BasicAuth(*auth_object)
    elif callable(auth_object):
        return auth_object
    else:
        raise ValueError("Invalid authentication strategy: %s" % auth_object)


class ApiTokenParam(object):
    """
    Authorizes requests using a token or key in a query parameter.
    Users should subclass this class to define which parameter is the token parameter.
    """
    def __init__(self, param, token):
        self._param = param
        self._param_value = token

    def __call__(self, request_builder):
        request_builder.info["params"][self._param] = self._param_value


# class ExampleApiTokenParam(ApiTokenParam):
#     _param = "api-token"
#     def __init__(self, token):
#         self._param_value = token


class ApiTokenHeader(object):
    """
    Authorizes requests using a token or key in a header.
    Users should subclass this class to define which header is the token header.
    The subclass may also, optionally, define a token prefix (such as in BearerToken)

    _header and/or _prefix may be defined as class attributes on subclasses,
    but should also override __init__() when they do so.
    """
    _header = None
    _prefix = None

    def __init__(self, header, token, prefix=None):
        self._header = header
        self._prefix = prefix
        self._token = token

    @property
    def _header_value(self):
        if self._prefix:
            return "%s %s" % (self._prefix, self._token)
        else:
            return self._token

    def __call__(self, request_builder):
        request_builder.info["headers"][self._header] = self._header_value


class BasicAuth(ApiTokenHeader):
    """Authorizes requests using HTTP Basic Authentication."""

    _header = "Authorization"

    def __init__(self, username, password):
        self._username = username
        self._password = password

    @property
    def _header_value(self):
        return auth._basic_auth_str(self._username, self._password)


class ProxyAuth(BasicAuth):
    """Authorizes requests with an intermediate HTTP proxy."""
    _header = "Proxy-Authorization"


class BearerToken(ApiTokenHeader):

    _header = "Authorization"
    _prefix = "Bearer"

    def __init__(self, token):
        self._token = token


class MultiAuth(object):
    """
    Authorizes requests using multiple auth methods at the same time.
        api_auth = MultiAuth(
            BasicAuth(username, password),
            ProxyAuth(proxy_user, proxy_pass)
        )
        api_consumer = SomeApiConsumerClass(
            "https://my.base_url.com/",
            auth=api_auth
        )

    Mostly, this is useful for API users to supply intermediary credentials (such as for a proxy).
    """
    def __init__(self, *auth_methods):
        self._auth_methods = [get_auth(auth_method) for auth_method in auth_methods]

    def __call__(self, request_builder):
        for auth_method in self._auth_methods:
            auth_method(request_builder)

    def __getitem__(self, index):
        return self._auth_methods[index]

    def __len__(self):
        return len(self._auth_methods)

    def append(self, auth_method):
        self._auth_methods.append(get_auth(auth_method))

    def extend(self, auth_methods):
        self._auth_methods.extend([get_auth(auth_method) for auth_method in auth_methods])
