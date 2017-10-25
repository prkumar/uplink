# Third party imports
import pytest

# Local imports
from uplink import client


@pytest.fixture
def http_client_mock(mocker):
    return mocker.Mock(spec=client.BaseHttpClient)


class TestPreparedRequest(object):

    def test_execute(self, mocker):
        backend_factory = mocker.Mock(spec=client.BackendFactory)
        backend_factory.sync_backend.send_request.return_value = True
        prepared = client.PreparedRequest(backend_factory, "request")
        response = prepared.execute()
        backend_factory.sync_backend.send_request.assert_called_with("request")
        assert response

    def test_enqueue(self, mocker):
        backend_factory = mocker.Mock(spec=client.BackendFactory)
        backend_factory.async_backend.send_request.return_value = True
        prepared = client.PreparedRequest(backend_factory, "request")
        response = prepared.enqueue()
        backend_factory.async_backend.send_request.assert_called_with("request")
        assert response


class TestRequest(object):

    def test_enter(self, http_client_mock):
        args = [1, 2, 3]
        request = client.Request(http_client_mock, args)
        with request as metadata:
            http_client_mock.audit_request.assert_called_with(*args)
            assert list(metadata) == args

    def test_fulfill(self, http_client_mock):
        request = client.Request(http_client_mock, ())
        request.fulfill(1)
        http_client_mock.handle_response.assert_called_with(1)


class TestBaseHttpClient(object):

    def test_handle_response(self):
        response = {}
        assert client.BaseHttpClient().handle_response(response) is response


class TestHttpClientDecorator(object):

    def test_delegate_audit_request(self, http_client_mock):
        connection = client.HttpClientDecorator(http_client_mock)
        connection.audit_request("method", "url", {})
        http_client_mock.audit_request.assert_called_with("method", "url", {})

    def test_delegate_handle_exception_request(self, http_client_mock):
        connection = client.HttpClientDecorator(http_client_mock)
        connection.handle_exception(1, 2, 3)
        http_client_mock.handle_exception.assert_called_with(1, 2, 3)

    def test_delegate_handle_response(self, http_client_mock):
        connection = client.HttpClientDecorator(http_client_mock)
        connection.handle_response({})
        http_client_mock.handle_response.assert_called_with({})

    def test_delegate_backend(self, http_client_mock):
        connection = client.HttpClientDecorator(http_client_mock)
        assert connection._backend is http_client_mock._backend
