# Local imports
from uplink import hooks

# TODO: Add test for `uplink.TransactionHookChain`


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


class TestTransactionHookChain(object):

    def test_delegate_audit_request(self, transaction_hook_mock):
        chain = hooks.TransactionHookChain(transaction_hook_mock)
        chain.audit_request("method", "url", {})
        transaction_hook_mock.audit_request.assert_called_with("method", "url", {})

    def test_delegate_handle_response(self, transaction_hook_mock):
        chain = hooks.TransactionHookChain(transaction_hook_mock)
        chain.handle_response({})
        transaction_hook_mock.handle_response.assert_called_with({})
