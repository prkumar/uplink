"""
This module defines an
"""


class BaseTransactionHook(object):

    def audit_request(self, method, url, extras):  # pragma: no cover
        pass

    def handle_response(self, response):
        return response


class TransactionHook(BaseTransactionHook):
    pass


class TransactionHookDecorator(BaseTransactionHook):
    """
    Decorator pattern for runtime modification of an API client's
    behavior.
    """

    def __init__(self, connection):
        assert isinstance(connection, BaseTransactionHook)
        self._connection = connection

    def __getattr__(self, item):  # pragma: no cover
        return getattr(self._connection, item)

    def audit_request(self, *args, **kwargs):
        self._connection.audit_request(*args, **kwargs)

    def handle_response(self, *args, **kwargs):
        return self._connection.handle_response(*args, **kwargs)


class TransactionHookChain(BaseTransactionHook):
    def __init__(self, *hooks):
        self._hooks = hooks

    def audit_request(self, *args, **kwargs):
        for hook in self._hooks:
            hook.audit_request(*args, **kwargs)

    def handle_response(self, response, *args, **kwargs):
        for hook in self._hooks:
            response = hook.handle_response(response, *args, **kwargs)
        return response


class RequestAuditor(BaseTransactionHook):
    def __init__(self, auditor):
        self._audit = auditor

    def audit_request(self, *args, **kwargs):
        return self._audit(*args, **kwargs)


class ResponseHandler(BaseTransactionHook):
    def __init__(self, handler):
        self._handle = handler

    def handle_response(self, *args, **kwargs):
        return self._handle(*args, **kwargs)
