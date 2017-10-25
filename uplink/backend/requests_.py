# Standard library imports
import atexit

# Local imports
from uplink.backend import interfaces

# Third party imports
import requests


class RequestsBackend(interfaces.Backend):
    def __init__(self):
        self._session = requests.Session()
        atexit.register(self._session.close)

    def send_request(self, request):
        with request as (method, url, extras):
            response = self._session.request(
                method=method,
                url=url,
                **extras
            )
            return request.fulfill(response)
