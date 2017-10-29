# Standard library imports
import atexit

# Local imports
from uplink.backend import interfaces

# Third party imports
import requests


class RequestsClient(interfaces.HttpClientAdapter):
    def __init__(self):
        self._session = requests.Session()
        atexit.register(self._session.close)

    @property
    def is_synchronous(self):
        return True

    def create_request(self):
        return Request(self._session)


class Request(interfaces.Request):

    def __init__(self, session):
        self._session = session
        self._callback = None

    def send(self, method, url, extras):
        response = self._session.request(
            method=method,
            url=url,
            **extras
        )
        if self._callback is not None:
            response = self._callback(response)
        return response

    def add_callback(self, callback):
        self._callback = callback
