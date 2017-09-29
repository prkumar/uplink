# Third party imports
import pytest

# Local imports
from uplink import client


@pytest.fixture
def http_client_mock(mocker):
    return mocker.Mock(spec=client.BaseHttpClient)


class TestPreparedRequest(object):

    def test_send(self, mocker):
        sender = mocker.stub(name="sender")
        sender.return_value = "hello"
        prepared = client.PreparedRequest(sender, "arg1", "arg2")
        response = prepared.send()
        sender.assert_called_with("arg1", "arg2")
        assert response is sender.return_value


class TestBaseHttpClient(object):

    def test_wrap_request(self, mocker):
        request = mocker.stub(name="request")
        connection = client.BaseHttpClient()
        connection.wrap_request(request)
        assert request.called

    def test_handle_response(self):
        response = {}
        assert client.BaseHttpClient().handle_response(response) is response


class TestHttpClientDecorator(object):

    def test_delegate_audit_request(self, http_client_mock):
        connection = client.HttpClientDecorator(http_client_mock)
        connection.audit_request("method", "url", {})
        http_client_mock.audit_request.assert_called_with("method", "url", {})

    def test_delegate_wrap_request(self, mocker, http_client_mock):
        request_mock = mocker.stub(name="request")
        connection = client.HttpClientDecorator(http_client_mock)
        connection.wrap_request(request_mock)
        http_client_mock.wrap_request.assert_called_with(request_mock)

    def test_delegate_handle_response(self, http_client_mock):
        connection = client.HttpClientDecorator(http_client_mock)
        connection.handle_response({})
        http_client_mock.handle_response.assert_called_with({})

    def test_delegate_request_sender(self, http_client_mock):
        connection = client.HttpClientDecorator(http_client_mock)
        assert connection._request_sender == http_client_mock._request_sender
