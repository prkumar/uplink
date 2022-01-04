# Third-party imports
import pytest

# Local imports
from uplink import auth
from uplink import utils


class TestGetAuth(object):
    def test_none(self):
        authentication = auth.get_auth(None)
        assert authentication == utils.no_op

    def test_tuple(self):
        authentication = auth.get_auth(("username", "password"))
        assert isinstance(authentication, auth.BasicAuth)

    def test_callable(self):
        def func():
            pass

        output = auth.get_auth(func)
        assert output is func

    def test_unsupported(self):
        with pytest.raises(ValueError):
            auth.get_auth(object())


def test_api_token_param(request_builder):
    # Setup
    token_param_auth = auth.ApiTokenParam(param="token-param", token="token-value")

    # Verify
    token_param_auth(request_builder)
    assert request_builder.info["params"]["token-param"] == "token-value"


def test_api_token_header_without_prefix(request_builder):
    # Setup
    token_header_auth = auth.ApiTokenHeader("Token-Header", "token-value")

    # Verify
    token_header_auth(request_builder)
    assert request_builder.info["headers"]["Token-Header"] == "token-value"


def test_api_token_header_with_prefix(request_builder):
    # Setup
    token_header_auth = auth.ApiTokenHeader("Token-Header", "token-value", prefix="Prefix")

    # Verify
    token_header_auth(request_builder)
    assert request_builder.info["headers"]["Token-Header"] == "Prefix token-value"


def test_api_token_header_subclass_without_prefix(request_builder):
    # Setup

    class ApiTokenHeaderSubclass(auth.ApiTokenHeader):
        _header = "Token-Header"

        def __init__(self, token):
            self._token = token

    token_header_auth = ApiTokenHeaderSubclass("token-value")

    # Verify
    token_header_auth(request_builder)
    assert request_builder.info["headers"]["Token-Header"] == "token-value"


def test_api_token_header_subclass_with_prefix(request_builder):
    # Setup

    class ApiTokenHeaderSubclass(auth.ApiTokenHeader):
        _header = "Token-Header"
        _prefix = "Prefix"

        def __init__(self, token):
            self._token = token

    token_header_auth = ApiTokenHeaderSubclass("token-value")

    # Verify
    token_header_auth(request_builder)
    assert request_builder.info["headers"]["Token-Header"] == "Prefix token-value"


def test_basic_auth(request_builder):
    # Setup
    basic_auth = auth.BasicAuth("username", "password")

    # Verify
    basic_auth(request_builder)
    auth_str = basic_auth._header_value
    assert request_builder.info["headers"]["Authorization"] == auth_str


def test_proxy_auth(request_builder):
    # Setup
    proxy_auth = auth.ProxyAuth("username", "password")

    # Verify
    proxy_auth(request_builder)
    auth_str = proxy_auth._header_value
    assert request_builder.info["headers"]["Proxy-Authorization"] == auth_str


def test_bearer_token(request_builder):
    # Setup
    bearer_token = auth.BearerToken("bearer-token")

    # Verify
    bearer_token(request_builder)
    auth_str = bearer_token._header_value
    assert request_builder.info["headers"]["Authorization"] == auth_str


class TestMultiAuth(object):
    def setup_basic_auth(self):
        return auth.BasicAuth("apiuser", "apipass")

    def verify_basic_auth(self, basic_auth, request_builder):
        basic_auth_str = basic_auth._header_value
        assert request_builder.info["headers"]["Authorization"] == basic_auth_str

    def setup_proxy_auth(self):
        return auth.ProxyAuth("proxyuser", "proxypass")

    def verify_proxy_auth(self, proxy_auth, request_builder):
        proxy_auth_str = proxy_auth._header_value
        assert request_builder.info["headers"]["Proxy-Authorization"] == proxy_auth_str

    def setup_param_auth(self):
        return auth.ApiTokenParam(param="token-param", token="token-value")

    def verify_param_auth(self, request_builder):
        assert request_builder.info["params"]["token-param"] == "token-value"

    def test_len(self):
        multi_auth = auth.MultiAuth()
        assert len(multi_auth) == 0

    def test_none(self):
        multi_auth = auth.MultiAuth(None)
        assert len(multi_auth) == 1
        assert multi_auth[0] == utils.no_op

    def test_one_method(self, request_builder):
        # Setup
        basic_auth = self.setup_basic_auth()
        multi_auth = auth.MultiAuth(basic_auth)

        # Verify
        assert len(multi_auth) == 1
        assert multi_auth[0] == basic_auth

        multi_auth(request_builder)
        self.verify_basic_auth(basic_auth, request_builder)

    def test_four_methods(self, request_builder):
        # Setup
        param_auth = self.setup_param_auth()
        basic_auth = self.setup_basic_auth()
        proxy_auth = self.setup_proxy_auth()
        multi_auth = auth.MultiAuth(None, param_auth, basic_auth, proxy_auth)

        # Verify
        assert len(multi_auth) == 4
        assert multi_auth[0] == utils.no_op
        assert multi_auth[1] == param_auth
        assert multi_auth[2] == basic_auth
        assert multi_auth[3] == proxy_auth

        multi_auth(request_builder)
        self.verify_param_auth(request_builder)
        self.verify_basic_auth(basic_auth, request_builder)
        self.verify_proxy_auth(proxy_auth, request_builder)

    def test_append(self, request_builder):
        # Setup
        basic_auth = self.setup_basic_auth()
        proxy_auth = self.setup_proxy_auth()
        multi_auth = auth.MultiAuth()
        multi_auth.append(basic_auth)
        multi_auth.append(proxy_auth)

        # Verify
        assert len(multi_auth) == 2
        assert multi_auth[0] == basic_auth
        assert multi_auth[1] == proxy_auth

        multi_auth(request_builder)
        self.verify_basic_auth(basic_auth, request_builder)
        self.verify_proxy_auth(proxy_auth, request_builder)

    def test_extend(self, request_builder):
        # Setup
        basic_auth = self.setup_basic_auth()
        proxy_auth = self.setup_proxy_auth()
        multi_auth = auth.MultiAuth()
        multi_auth.extend([basic_auth, proxy_auth])

        # Verify
        assert len(multi_auth) == 2
        assert multi_auth[0] == basic_auth
        assert multi_auth[1] == proxy_auth

        multi_auth(request_builder)
        self.verify_basic_auth(basic_auth, request_builder)
        self.verify_proxy_auth(proxy_auth, request_builder)
