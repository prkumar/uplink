# Standard library imports
import atexit
import asyncio

# Third party imports
import aiohttp

# Local imports
from uplink.clients import interfaces


class AiohttpClient(interfaces.HttpClientAdapter):

    def __init__(self, session=None):
        # TODO: Remove hardcoded connector initialization.
        if session is None:
            session = aiohttp.ClientSession()
            atexit.register(session.close)
        self._session = session

    def create_request(self):
        return Request(self._session)


class Request(interfaces.Request):

    def __init__(self, session):
        self._session = session
        self._callback = None

    # noinspection Annotator
    @asyncio.coroutine
    def send(self, method, url, extras):
        response = yield from self._session.request(method, url, **extras)
        if self._callback is not None:
            response = self._callback(response)
        return response

    def add_callback(self, callback):
        self._callback = callback
