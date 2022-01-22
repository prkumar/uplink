# Standard library imports
import contextlib

# Third-party imports
import pytest

# Local imports
from uplink.clients import (
    interfaces,
    requests_,
    twisted_,
    register,
    io,
)


@contextlib.contextmanager
def _patch(obj, attr, value):
    if obj is not None:
        old_value = getattr(obj, attr)
        setattr(obj, attr, value)
    yield
    if obj is not None:
        setattr(obj, attr, old_value)


def test_get_default_client_with_non_callable():
    # Setup
    old_default = register.get_default_client()
    register.set_default_client("client")
    default_client = register.get_default_client()
    register.set_default_client(old_default)

    # Verify: an object that is not callable should be returned as set.
    assert default_client == "client"


def test_get_client_with_http_client_adapter_subclass():
    class HttpClientAdapterMock(interfaces.HttpClientAdapter):
        pass

    client = register.get_client(HttpClientAdapterMock)
    assert isinstance(client, HttpClientAdapterMock)


def test_get_client_with_unrecognized_key():
    assert register.get_client("no client for this key") is None


class TestRequests(object):
    def test_get_client(self, mocker):
        import requests

        session_mock = mocker.Mock(spec=requests.Session)
        client = register.get_client(session_mock)
        assert isinstance(client, requests_.RequestsClient)

    def test_init_with_kwargs(self):
        session = requests_.RequestsClient._create_session(
            cred=("username", "password")
        )
        assert session.cred == ("username", "password")

    def test_client_send(self, mocker):
        # Setup
        import requests

        session_mock = mocker.Mock(spec=requests.Session)
        session_mock.request.return_value = "response"
        callback = mocker.stub()
        client = requests_.RequestsClient(session_mock)

        # Run
        response = client.send(("method", "url", {}))

        # Verify
        session_mock.request.assert_called_with(method="method", url="url")

        # Run callback
        client.apply_callback(callback, response)
        callback.assert_called_with(session_mock.request.return_value)

    def test_dont_close_provided_session(self, mocker):
        # Setup
        import requests
        import gc

        session_mock = mocker.Mock(spec=requests.Session)
        session_mock.request.return_value = "response"

        # Run
        client = requests_.RequestsClient(session_mock)
        client.send(("method", "url", {}))
        del client
        gc.collect()

        assert session_mock.close.call_count == 0

    def test_close_auto_generated_session(self, mocker):
        # Setup
        import requests
        import gc

        session_mock = mocker.Mock(spec=requests.Session)
        session_mock.request.return_value = "response"
        session_cls_mock = mocker.patch("requests.Session")
        session_cls_mock.return_value = session_mock

        # Run
        client = requests_.RequestsClient()
        client.send(("method", "url", {}))
        del client
        gc.collect()

        assert session_mock.close.call_count == 1

    def test_exceptions(self):
        import requests

        exceptions = requests_.RequestsClient.exceptions

        with pytest.raises(exceptions.BaseClientException):
            raise requests.RequestException()

        with pytest.raises(exceptions.BaseClientException):
            # Test polymorphism
            raise requests.exceptions.InvalidURL()

        with pytest.raises(exceptions.ConnectionError):
            raise requests.exceptions.ConnectionError()

        with pytest.raises(exceptions.ConnectionTimeout):
            raise requests.exceptions.ConnectTimeout()

        with pytest.raises(exceptions.ServerTimeout):
            raise requests.exceptions.ReadTimeout()

        with pytest.raises(exceptions.SSLError):
            raise requests.exceptions.SSLError()

        with pytest.raises(exceptions.InvalidURL):
            raise requests.exceptions.InvalidURL()

    def test_io(self):
        assert isinstance(requests_.RequestsClient.io(), io.BlockingStrategy)


class TestTwisted(object):
    def test_init_without_client(self):
        twisted = twisted_.TwistedClient()
        assert isinstance(twisted._proxy, requests_.RequestsClient)

    def test_create_requests_no_twisted(self, http_client_mock):
        with _patch(twisted_, "threads", None):
            with pytest.raises(NotImplementedError):
                twisted_.TwistedClient(http_client_mock)

    def test_client_send(self, mocker, http_client_mock):
        deferToThread = mocker.patch.object(twisted_.threads, "deferToThread")
        request = twisted_.TwistedClient(http_client_mock)
        request.send((1, 2, 3))
        deferToThread.assert_called_with(http_client_mock.send, (1, 2, 3))

    def test_client_callback(self, mocker, http_client_mock):
        # Setup
        callback = mocker.stub()
        deferred = mocker.Mock()
        deferToThread = mocker.patch.object(twisted_.threads, "deferToThread")
        deferToThread.return_value = deferred
        client = twisted_.TwistedClient(http_client_mock)

        # Run
        response = client.apply_callback(callback, 1)

        # Verify
        assert response is deferred
        deferToThread.assert_called_with(
            http_client_mock.apply_callback, callback, 1
        )

    def test_exceptions(self, http_client_mock):
        twisted_client = twisted_.TwistedClient(http_client_mock)
        assert http_client_mock.exceptions == twisted_client.exceptions

    def test_io(self):
        assert isinstance(twisted_.TwistedClient.io(), io.TwistedStrategy)
