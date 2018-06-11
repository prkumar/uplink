"""This module implements the auth layer."""

# Standard library imports
import collections

# Third-party imports
from requests import auth

# Local imports
from uplink import utils

__all__ = []


def get_auth(auth_object=None):
    if auth_object is None:
        return utils.no_op
    elif isinstance(auth_object, collections.Iterable):
        return BasicAuth(*auth_object)
    elif callable(auth_object):
        return auth_object
    else:
        raise ValueError("Invalid authentication strategy: %s" % auth_object)


class BasicAuth(object):
    """Authorizes requests using HTTP Basic Authentication."""

    def __init__(self, username, password):
        self._username = username
        self._password = password

    @property
    def _auth_str(self):
        return auth._basic_auth_str(self._username, self._password)

    def __call__(self, request_builder):
        request_builder.info["headers"]["Authorization"] = self._auth_str


class ProxyAuth(BasicAuth):
    def __call__(self, request_builder):
        request_builder.info["headers"]["Proxy-Authorization"] = self._auth_str


class BearerToken(object):
    def __init__(self, token):
        self._auth_str = "Bearer %s" % token

    def __call__(self, request_builder):
        request_builder.info["headers"]["Authorization"] = self._auth_str
