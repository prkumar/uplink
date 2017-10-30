# Third party imports
from twisted.internet import threads

# Local imports
from uplink.backend import requests_
from uplink.backend import interfaces


class TwistedClient(interfaces.HttpClientAdapter):

    def __init__(self, client=None):
        if client is None:
            client = requests_.RequestsClient()
        self._requests = client

    def is_synchronous(self):
        return False

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
