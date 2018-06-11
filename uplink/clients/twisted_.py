"""
This module defines an :py:class:`aiohttp.ClientSession` adapter that
returns :py:class:`twisted.internet.defer.Deferred` responses.
"""

# Third party imports
try:
    from twisted.internet import threads
except ImportError:  # pragma: no cover
    threads = None

# Local imports
from uplink.clients import helpers, interfaces, register


class TwistedClient(interfaces.HttpClientAdapter):
    """
    Client that returns :py:class:`twisted.internet.defer.Deferred`
    responses.

    Note:
        This client is an optional feature and requires the :py:mod:`twisted`
        package. For example, here's how to install this extra using pip::

            $ pip install uplink[twisted]

    Args:
        session (:py:class:`requests.Session`, optional): The session
            that should handle sending requests. If this argument is
            omitted or set to :py:obj:`None`, a new session will be
            created.
    """

    def __init__(self, session=None):
        if threads is None:
            raise NotImplementedError("twisted is not installed.")
        self._requests = register.get_client(session)

    def create_request(self):
        return Request(self._requests.create_request())


class Request(helpers.ExceptionHandlerMixin, interfaces.Request):
    def __init__(self, proxy):
        self._proxy = proxy
        self._callback = None

    def send(self, method, url, extras):
        deferred = threads.deferToThread(self._proxy.send, method, url, extras)
        if self._callback is not None:
            deferred.addCallback(self._callback)
        deferred.addErrback(self.handle_failure)
        return deferred

    def add_callback(self, callback):
        self._callback = callback

    def handle_failure(self, failure):
        tb = failure.getTracebackObject()
        self._exception_handler.handle(failure.type, failure.value, tb)
        failure.raiseException()
