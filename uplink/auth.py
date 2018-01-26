"""This module implements the auth layer."""

# Standard library imports
import collections

# Third-party imports
from requests import auth


def get_auth(auth_object):
    if isinstance(auth_object, collections.Iterable):
        return HttpBasicAuth(*auth_object)
    elif callable(auth_object):
        return auth_object
    else:
        # TODO: Raise a more explicit error (?)
        raise ValueError("Invalid auth object: %s" % repr(auth_object))


class HttpBasicAuth(object):
    """Authorizes requests using HTTP Basic Authentication."""

    def __init__(self, username, password):
        self._username = username
        self._password = password

    @property
    def _auth_str(self):
        return auth._basic_auth_str(
            self._username,
            self._password
        )

    def __call__(self, request_builder):
        request_builder.info["headers"]["Authorization"] = self._auth_str


class HttpProxyAuth(HttpBasicAuth):

    def __call__(self, request_builder):
        request_builder.info["headers"]["Proxy-Authorization"] = self._auth_str
