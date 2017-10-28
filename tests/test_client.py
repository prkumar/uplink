# Third party imports
import pytest

# Local imports
from uplink import client


class TestBaseHttpClient(object):

    def test_handle_response(self):
        r = {}
        assert client.BaseTransactionHook().handle_response(r) is r


class TestHttpClientDecorator(object):

    def test_delegate_audit_request(self, transaction_hook_mock):
        connection = client.TransactionHookDecorator(transaction_hook_mock)
        connection.audit_request("method", "url", {})
        transaction_hook_mock.audit_request.assert_called_with("method", "url", {})

    def test_delegate_handle_response(self, transaction_hook_mock):
        connection = client.TransactionHookDecorator(transaction_hook_mock)
        connection.handle_response({})
        transaction_hook_mock.handle_response.assert_called_with({})
