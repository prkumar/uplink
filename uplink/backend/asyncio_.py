# Standard library imports
import atexit
import asyncio

# Third party imports
import aiohttp

# Local imports
from uplink.backend import interfaces


# TODO: Is there a way to decorate this co-routine so we can still await it?

class AsyncioBackend(interfaces.Backend):
    def __init__(self, *args, **kwargs):
        # TODO: Remove hardcoded connector initialization.
        self._args = args
        self._kwargs = kwargs
        self._kwargs["connector"] = aiohttp.TCPConnector(verify_ssl=False)
        self._session = aiohttp.ClientSession(*args, **kwargs)
        atexit.register(self._session.close)

    @asyncio.coroutine
    def send_request(self, request):
        with request as (method, url, extras):
            resp = yield from self._session.request(method, url, **extras)
            return request.fulfill(resp)
