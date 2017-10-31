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

    def audit_request(self, method, url, extras):
        self._connection.audit_request(method, url, extras)

    def handle_response(self, response):
        return self._connection.handle_response(response)
