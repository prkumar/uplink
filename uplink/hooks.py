"""
This module provides a class for defining custom handling for specific
points of an HTTP transaction.
"""

__all__ = [
    "TransactionHook",
    "RequestAuditor",
    "ResponseHandler"
]


class TransactionHook(object):
    """
    A utility class providing methods that define hooks for specific
    points of an HTTP transaction.
    """

    def audit_request(self, request_builder):  # pragma: no cover
        """Inspects details of a request before it is sent."""
        pass

    handle_response = None
    """
    Handles a response object from the server.

    Args:
        response: The received HTTP response.
    """

    def handle_exception(self, exc_type, exc_val, exc_tb):  # pragma: no cover
        """
        Handles an exception thrown while waiting for a response from
        the server.

        Args:
            exc_type: The type of the exception.
            exc_val: The exception instance raised.
            exc_tb: A traceback instance.
        """
        pass


class TransactionHookChain(TransactionHook):
    """
    A chain that conjoins several transaction hooks into a single
    object.

    A method call on this composite object invokes the corresponding
    method on all hooks in the chain.
    """

    def __init__(self, *hooks):
        self._hooks = hooks

        # TODO: Add comment about why we are doing this.
        response_handlers = [h for h in hooks if h.handle_response is not None]
        if not response_handlers:
            self.handle_response = None
        elif len(response_handlers) == 1:
            self.handle_response = response_handlers[0].handle_response

    def audit_request(self, *args, **kwargs):
        for hook in self._hooks:
            hook.audit_request(*args, **kwargs)

    def handle_response(self, response, *args, **kwargs):
        for hook in self._hooks:
            response = hook.handle_response(response, *args, **kwargs)
        return response

    def handle_exception(self, *args, **kwargs):
        for hook in self._hooks:
            hook.handle_exception(*args, **kwargs)


class RequestAuditor(TransactionHook):
    """
    Transaction hook that inspects requests using a function provided at
    time of instantiation.
    """

    def __init__(self, auditor):
        self.audit_request = auditor


class ResponseHandler(TransactionHook):
    """
    Transaction hook that handles responses using a function provided at
    time of instantiation.
    """

    def __init__(self, handler):
        self.handle_response = handler


class ExceptionHandler(TransactionHook):
    """
    Transaction hook that handles an exception thrown while waiting for
    a response, using the provided function.
    """

    def __init__(self, exception_handler):
        self.handle_exception = exception_handler
