# Third party imports
import pytest

# Local imports
from uplink import hooks


class TestTransactionHook(object):
    def test_handle_response(self):
        r = {}
        assert hooks.TransactionHook().handle_response(r) is r


class TestResponseHandler(object):
    def test_handle_response(self, mocker):
        converter = mocker.Mock()
        input_value = "converted"
        converter.return_value = input_value
        rc = hooks.ResponseHandler(converter)
        assert rc.handle_response(None) is input_value


class TestRequestAuditor(object):
    def test_audit_request(self, mocker):
        auditor = mocker.stub()
        ra = hooks.RequestAuditor(auditor)
        ra.audit_request(1, 2, 3)
        auditor.assert_called_with(1, 2, 3)


class TestExceptionHandler(object):
    def test_handle_exception(self, mocker):
        handler = mocker.stub()
        eh = hooks.ExceptionHandler(handler)
        eh.handle_exception(1, 2, 3)
        handler.assert_called_with(1, 2, 3)


class TestTransactionHookChain(object):

    def test_delegate_audit_request(self, transaction_hook_mock):
        chain = hooks.TransactionHookChain(transaction_hook_mock)
        chain.audit_request("method", "url", {})
        transaction_hook_mock.audit_request.assert_called_with("method", "url", {})

    def test_delegate_handle_response(self, transaction_hook_mock):
        chain = hooks.TransactionHookChain(transaction_hook_mock)
        chain.handle_response({})
        transaction_hook_mock.handle_response.assert_called_with({})

    def test_delegate_handle_response_multiple(self, transaction_hook_mock):
        chain = hooks.TransactionHookChain(
            transaction_hook_mock, transaction_hook_mock)
        chain.handle_response({})
        transaction_hook_mock.call_count == 2

    def test_delegate_handle_exception(self, transaction_hook_mock):
        chain = hooks.TransactionHookChain(transaction_hook_mock)
        chain.handle_exception(None, None, None)
        transaction_hook_mock.handle_exception.assert_called_with(
            None, None, None
        )