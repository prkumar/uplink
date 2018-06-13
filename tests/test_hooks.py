# Local imports
from uplink import hooks


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
        transaction_hook_mock.audit_request.assert_called_with(
            "method", "url", {}
        )

    def test_delegate_handle_response(self, transaction_hook_mock):
        chain = hooks.TransactionHookChain(transaction_hook_mock)
        chain.handle_response({})
        transaction_hook_mock.handle_response.assert_called_with({})

    def test_delegate_handle_response_multiple(self, mocker):
        # Include one hook that can't handle responses
        mock_response_handler = mocker.stub()
        mock_request_auditor = mocker.stub()

        chain = hooks.TransactionHookChain(
            hooks.RequestAuditor(mock_request_auditor),
            hooks.ResponseHandler(mock_response_handler),
            hooks.ResponseHandler(mock_response_handler),
        )
        chain.handle_response({})
        mock_response_handler.call_count == 2
        mock_request_auditor.call_count == 1

    def test_delegate_handle_exception(self, transaction_hook_mock):
        chain = hooks.TransactionHookChain(transaction_hook_mock)
        chain.handle_exception(None, None, None)
        transaction_hook_mock.handle_exception.assert_called_with(
            None, None, None
        )
