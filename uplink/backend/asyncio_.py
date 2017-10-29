# Standard library imports
import atexit
import asyncio

# Third party imports
import aiohttp

# Local imports
from uplink.backend import interfaces


class AsyncioClient(interfaces.HttpClientAdapter):
    def __init__(self, *args, **kwargs):
        # TODO: Remove hardcoded connector initialization.
        self._args = args
        self._kwargs = kwargs
        self._kwargs["connector"] = aiohttp.TCPConnector(verify_ssl=False)
        self._session = aiohttp.ClientSession(*args, **kwargs)
        atexit.register(self._session.close)

    @property
    def is_synchronous(self):
        return False

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
