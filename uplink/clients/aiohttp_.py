"""
This module defines an :py:class:`aiohttp.ClientSession` adapter
that sends awaitable requests.
"""
# Standard library imports
import atexit
import asyncio
import threading

from concurrent import futures

# Third party imports
import aiohttp

# Local imports
from uplink.clients import interfaces


def threaded_callback(callback):
    coroutine_callback = asyncio.coroutine(callback)

    @asyncio.coroutine
    def new_callback(response):
        yield from response.text()
        response = ThreadedResponse(response)
        response = yield from coroutine_callback(response)
        if isinstance(response, ThreadedResponse):
            return response.unwrap()
        else:
            return response

    return new_callback


class AiohttpClient(interfaces.HttpClientAdapter):
    """
    An :py:mod:`aiohttp` client adapter that creates awaitable
    responses.

    Args:
        session (:py:class:`aiohttp.ClientSession`, optional):
            A :py:mod:`aiohttp` client session that should handle
            sending requests. If this argument is not explicitly
            set, a new session will created automatically.
    """

    def __init__(self, session=None, _sync_callback_adapter=threaded_callback):
        self._session = session
        self._sync_callback_adapter = _sync_callback_adapter

    def create_request(self):
        return Request(self)

    @asyncio.coroutine
    def session(self):
        """Returns a `aiohttp.ClientSession` to send awaitable requests."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
            atexit.register(self._session.close)
        return self._session

    def wrap_callback(self, callback):
        if not asyncio.iscoroutinefunction(callback):
            callback = self._sync_callback_adapter(callback)
        return callback


class Request(interfaces.Request):

    def __init__(self, client):
        self._client = client
        self._callback = None

    @asyncio.coroutine
    def send(self, method, url, extras):
        session = yield from self._client.session()
        response = yield from session.request(method, url, **extras)
        if self._callback is not None:
            response = yield from self._execute_callback(response)
        return response

    def add_callback(self, callback):
        self._callback = callback

    @asyncio.coroutine
    def _execute_callback(self, response):
        return (yield from self._client.wrap_callback(self._callback)(response))


class ThreadedCoroutine(object):

    def __init__(self, coroutine):
        self.__coroutine = coroutine

    def __call__(self, *args, **kwargs):
        with AsyncioExecutor() as executor:
            future = executor.submit(self.__coroutine, *args, **kwargs)
            result = future.result()
        return result


class ThreadedResponse(object):

    def __init__(self, response):
        self.__response = response

    def __getattr__(self, item):
        value = getattr(self.__response, item)
        if asyncio.iscoroutinefunction(value):
            return ThreadedCoroutine(value)
        return value

    def unwrap(self):
        return self.__response


class AsyncioExecutor(futures.Executor):
    """
    Executor that runs asyncio coroutines in a shadow thread.

    Credit to Vincent Michel, who wrote the original implementation:
    https://gist.github.com/vxgmichel/d16e66d1107a369877f6ef7e646ac2e5
    """

    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._target)
        self._thread.start()

    def _target(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def submit(self, fn, *args, **kwargs):
        coro = fn(*args, **kwargs)
        return asyncio.run_coroutine_threadsafe(coro, self._loop)

    def shutdown(self, wait=True):
        self._loop.call_soon_threadsafe(self._loop.stop)
        if wait:
            self._thread.join()
