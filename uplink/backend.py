# Standard library imports
import atexit

# Third-party imports
import requests


class RequestsBackend(object):
    def __init__(self):
        self._session = requests.Session()
        atexit.register(self._session.close)

    def send_request(self, method, url, extras):
        return self._session.request(
            method=method,
            url=url,
            **extras
        )

    def send_async_request(self, method, url, extras, callback):
        raise NotImplementedError
