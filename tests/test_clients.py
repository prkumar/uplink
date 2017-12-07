# Standard library imports
import sys

# Third party imports
import pytest
import inspect

# Local imports
from uplink.clients import requests_, twisted_

try:
    from uplink.clients import aiohttp_
except (ImportError, SyntaxError):
    aiohttp_ = None


requires_aiohttp = pytest.mark.skipif(
    not aiohttp_, reason="Requires Python 3.4 or above")


class TestTwisted(object):

    def test_init_without_client(self):
        twisted = twisted_.TwistedClient()
        assert isinstance(twisted._requests, requests_.RequestsClient)

    def test_create_requests(self, http_client_mock):
        twisted = twisted_.TwistedClient(http_client_mock)
        request = twisted.create_request()
        assert request._proxy is http_client_mock.create_request()
        assert isinstance(request, twisted_.Request)

    def test_create_requests_no_twisted(self, mocker, http_client_mock):
        twisted = twisted_.TwistedClient(http_client_mock)

        old_threads = twisted_.threads
        twisted_.threads = None
        with pytest.raises(NotImplementedError):
            twisted.create_request()
        twisted_.threads = old_threads

    def test_request_send(self, mocker,  request_mock):
        deferToThread = mocker.patch.object(twisted_.threads, "deferToThread")
        request = twisted_.Request(request_mock)
        request.send(1, 2, 3)
        deferToThread.assert_called_with(request_mock.send, 1, 2, 3)

    def test_request_send_with_callback(self, mocker, request_mock):
        # Setup
        callback = mocker.stub()
        deferred = mocker.Mock()
        deferToThread = mocker.patch.object(twisted_.threads, "deferToThread")
        deferToThread.return_value = deferred
        request = twisted_.Request(request_mock)
        request.add_callback(callback)

        # Run
        request.send(1, 2, 3)

        # Verify
        deferred.addCallback.assert_called_with(callback)
        deferToThread.assert_called_with(request_mock.send, 1, 2, 3)


@pytest.fixture
def aiohttp_session_mock(mocker):
    return mocker.Mock()


class TestAiohttp(object):

    @requires_aiohttp
    def test_create_request(self, aiohttp_session_mock):
        aiohttp = aiohttp_.AiohttpClient(aiohttp_session_mock)
        assert isinstance(aiohttp.create_request(), aiohttp_.Request)

    @requires_aiohttp
    def test_request_send(self, aiohttp_session_mock):
        aiohttp_session_mock.request.return_value = [0]
        client = aiohttp_.AiohttpClient(aiohttp_session_mock)
        request = aiohttp_.Request(client)
        response = request.send(1, 2, {})
        assert inspect.isgenerator(response)
        assert list(response) == [0]

    @requires_aiohttp
    def test_callback(self, aiohttp_session_mock):
        import asyncio

        @asyncio.coroutine
        def request(*args, **kwargs):
            return 2

        aiohttp_session_mock.request = request
        client = aiohttp_.AiohttpClient(aiohttp_session_mock, asyncio.coroutine)
        request = aiohttp_.Request(client)
        request.add_callback(lambda x: 2)
        response = request.send(1, 2, {})
        assert inspect.isgenerator(response)
        list(response)
        try:
            next(response)
        except StopIteration as err:
            err.value == 2
        else:
            assert False

    @requires_aiohttp
    def test_threaded_callback(self, mocker):
        import asyncio

        def callback(response):
            return response

        @asyncio.coroutine
        def response_text():
            pass

        # Mock response.
        response = mocker.Mock()
        response.text = mocker.stub(response_text)

        # Run
        new_callback = aiohttp_.threaded_callback(callback)
        return_value = new_callback(response)
        list(return_value)

        # Verify
        response.text.assert_called_with()
        try:
            next(return_value)
        except StopIteration as err:
            err.value == 2
        else:
            assert False

    @requires_aiohttp
    def test_threaded_coroutine(self):
        # Setup
        import asyncio

        @asyncio.coroutine
        def coroutine():
            return 1

        threaded_coroutine = aiohttp_.ThreadedCoroutine(coroutine)

        # Run -- should block
        response = threaded_coroutine()

        # Verify
        assert response == 1

    @requires_aiohttp
    def test_threaded_response(self, mocker):
        # Setup
        import asyncio

        @asyncio.coroutine
        def coroutine():
            return 1

        response = mocker.Mock()
        response.text = coroutine
        threaded_response = aiohttp_.ThreadedResponse(response)

        # Run
        threaded_coroutine = threaded_response.text
        return_value = threaded_coroutine()

        # Verify
        assert isinstance(threaded_coroutine, aiohttp_.ThreadedCoroutine)
        assert return_value == 1






