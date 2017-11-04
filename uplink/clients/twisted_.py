# Third party imports

try:
    from twisted.internet import threads
except ImportError:
    threads = None

# Local imports
from uplink.clients import requests_
from uplink.clients import interfaces


class TwistedClient(interfaces.HttpClientAdapter):

    def __init__(self, client=None):
        if client is None:
            client = requests_.RequestsClient()
        self._requests = client

    def create_request(self):
        if threads is None:
            raise NotImplementedError(
                "TwistedClient is not installed."
            )
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
