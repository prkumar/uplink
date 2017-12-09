# Third party imports
try:
    from twisted.internet import threads
except ImportError:
    threads = None

# Local imports
from uplink.clients import interfaces, register


class TwistedClient(interfaces.HttpClientAdapter):
    """
    Client that returns :py:class:`twisted.internet.defer.Deferred`
    responses.

    Args:
        session (:py:class:`requests.Session`, optional): The session
            that should handle sending requests. If this argument is
            omitted or set to :py:obj:`None`, a new session will be
            created.
    """

    def __init__(self, session=None):
        if threads is None:
            raise NotImplementedError("TwistedClient is not installed.")
        self._requests = register.get_client(session)

    def create_request(self):
        return Request(self._requests.create_request())


class Request(interfaces.Request):

    def __init__(self, proxy):
        self._proxy = proxy
        self._callback = None

    def send(self, method, url, extras):
        deferred = threads.deferToThread(
            self._proxy.send,
            method,
            url,
            extras
        )
        if self._callback is not None:
            deferred.addCallback(self._callback)
        return deferred

    def add_callback(self, callback):
        self._callback = callback
