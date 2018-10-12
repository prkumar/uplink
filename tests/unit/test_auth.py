# Third party imports
import pytest

# Local imports
from uplink import auth


class TestGetAuth(object):
    def test_tuple(self):
        authentication = auth.get_auth(("username", "password"))
        assert isinstance(authentication, auth.BasicAuth)

    def test_callable(self):
        def func():
            None

        output = auth.get_auth(func)
        assert output is func

    def test_unsupported(self):
        with pytest.raises(ValueError):
            auth.get_auth(object())


def test_basic_auth(request_builder):
    # Setup
    basic_auth = auth.BasicAuth("username", "password")

    # Verify
    basic_auth(request_builder)
    auth_str = basic_auth._auth_str
    assert request_builder.info["headers"]["Authorization"] == auth_str


def test_proxy_auth(request_builder):
    # Setup
    proxy_auth = auth.ProxyAuth("username", "password")

    # Verify
    proxy_auth(request_builder)
    auth_str = proxy_auth._auth_str
    assert request_builder.info["headers"]["Proxy-Authorization"] == auth_str


def test_bearer_token(request_builder):
    # Setup
    bearer_token = auth.BearerToken("bearer-token")

    # Verify
    bearer_token(request_builder)
    auth_str = bearer_token._auth_str
    assert request_builder.info["headers"]["Authorization"] == auth_str
