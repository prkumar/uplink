# Standard library imports
import contextlib

# Third party imports
import pytest

# Local imports
from uplink.clients import (
    AiohttpClient, helpers, interfaces, register, requests_, twisted_,
    exceptions
)

try:
    from uplink.clients import aiohttp_
except (ImportError, SyntaxError):
    aiohttp_ = None


requires_python34 = pytest.mark.skipif(
    not aiohttp_,
    reason="Requires Python 3.4 or above")


@contextlib.contextmanager
def _patch(obj, attr, value):
    if obj is not None:
        old_value = getattr(obj, attr)
        setattr(obj, attr, value)
    yield
    if obj is not None:
        setattr(obj, attr, old_value)


def test_get_default_client_with_non_callable():
    # Setup
    old_default = register.get_default_client()
    register.set_default_client("client")
    default_client = register.get_default_client()
    register.set_default_client(old_default)

    # Verify: an object that is not callable should be returned as set.
    assert default_client == "client"


def test_get_client_with_http_client_adapter_subclass():
    class HttpClientAdapterMock(interfaces.HttpClientAdapter):
        def create_request(self):
            pass

    client = register.get_client(HttpClientAdapterMock)
    assert isinstance(client, HttpClientAdapterMock)


def test_raise_exception():
    # FIXME: Loop through all registered client exceptions
    # Ensure that client errors are caught with proxy exception
    handler = helpers.ExceptionHandler()
    error = requests_.requests.ConnectionError()

    # Catch with proxy exception class
    with pytest.raises(exceptions.ConnectionError):
        with handler:
            raise error

    # Catch with original exception class
    with pytest.raises(requests_.requests.ConnectionError):
        with handler:
            raise error

    # Catch with proxy exception superclass
    with pytest.raises(exceptions.BaseClientException):
        with handler:
            raise error

    # Can't catch other exceptions
    with pytest.raises(exceptions.InvalidURL):
        try:
            with handler:
                raise exceptions.InvalidURL()
        except exceptions.ConnectionError:
            assert False


class TestRequests(object):

    def test_get_client(self, mocker):
        import requests
        session_mock = mocker.Mock(spec=requests.Session)
        client = register.get_client(session_mock)
        assert isinstance(client, requests_.RequestsClient)

    def test_init_with_kwargs(self):
        session = requests_.RequestsClient._create_session(
            cred=("username", "password")
        )
        assert session.cred == ("username", "password")

    def test_create_request(self):
        client = requests_.RequestsClient()
        request = client.create_request()
        assert isinstance(request, requests_.Request)

    def test_request_send(self, mocker):
        # Setup
        import requests
        session_mock = mocker.Mock(spec=requests.Session)
        session_mock.request.return_value = "response"
        callback = mocker.stub()
        client = requests_.Request(session_mock)
        client.add_callback(callback)

        # Run
        client.send("method", "url", {})

        # Verify
        session_mock.request.assert_called_with(method="method", url="url")
        callback.assert_called_with(session_mock.request.return_value)


class TestTwisted(object):

    def test_init_without_client(self):
        twisted = twisted_.TwistedClient()
        assert isinstance(twisted._requests, requests_.RequestsClient)

    def test_create_requests(self, http_client_mock):
        twisted = twisted_.TwistedClient(http_client_mock)
        request = twisted.create_request()
        assert request._proxy is http_client_mock.create_request()
        assert isinstance(request, twisted_.Request)

    def test_create_requests_no_twisted(self, http_client_mock):
        with _patch(twisted_, "threads", None):
            with pytest.raises(NotImplementedError):
                twisted_.TwistedClient(http_client_mock)

    def test_request_send(self, mocker,  request_mock):
        deferToThread = mocker.patch.object(twisted_.threads, "deferToThread")
        request = twisted_.Request(request_mock)
        request.send(1, 2, 3)
        deferToThread.assert_called_with(request_mock.send, 1, 2, 3)

    def test_request_send_callback_and_exception(self, mocker, request_mock):
        # Setup
        callback = mocker.stub()
        exception_handler = mocker.stub()
        deferred = mocker.Mock()
        deferToThread = mocker.patch.object(twisted_.threads, "deferToThread")
        deferToThread.return_value = deferred
        request = twisted_.Request(request_mock)
        request.add_callback(callback)
        request.add_exception_handler(exception_handler)

        # Run
        request.send(1, 2, 3)

        # Verify
        deferred.addCallback.assert_called_with(callback)
        deferred.addErrback(request.handle_failure)
        deferToThread.assert_called_with(request_mock.send, 1, 2, 3)

    def test_handle_failure(self, mocker, request_mock):
        # Setup
        failure = mocker.Mock(stub=twisted_.threads.failure.Failure)
        failure.type, failure.value = Exception, Exception()
        exception_handler = mocker.stub()
        request = twisted_.Request(request_mock)
        request.add_exception_handler(exception_handler)

        # Run
        request.handle_failure(failure)

        # Verify
        exception_handler.assert_called_with(
            failure.type, failure.value, failure.getTracebackObject()
        )


@pytest.fixture
def aiohttp_session_mock(mocker):
    import aiohttp
    return mocker.Mock(spec=aiohttp.ClientSession)


class TestAiohttp(object):

    @requires_python34
    def test_init_when_aiohttp_is_not_installed(self):
        with _patch(aiohttp_, "aiohttp", None):
            with pytest.raises(NotImplementedError):
                AiohttpClient()

    @requires_python34
    def test_get_client(self, aiohttp_session_mock):
        client = register.get_client(aiohttp_session_mock)
        assert isinstance(client, aiohttp_.AiohttpClient)

    @requires_python34
    def test_create_request(self, aiohttp_session_mock):
        aiohttp = aiohttp_.AiohttpClient(aiohttp_session_mock)
        assert isinstance(aiohttp.create_request(), aiohttp_.Request)

    @requires_python34
    def test_request_send(self, aiohttp_session_mock):
        # Setup
        import asyncio

        @asyncio.coroutine
        def request(*args, **kwargs):
            return 0

        aiohttp_session_mock.request = request
        client = aiohttp_.AiohttpClient(aiohttp_session_mock)
        request = aiohttp_.Request(client)

        # Run
        response = request.send(1, 2, {})
        loop = asyncio.get_event_loop()
        value = loop.run_until_complete(asyncio.ensure_future(response))

        # Verify
        assert value == 0

    @requires_python34
    def test_callback(self, aiohttp_session_mock):
        # Setup
        import asyncio

        @asyncio.coroutine
        def request(*args, **kwargs):
            return 2

        aiohttp_session_mock.request = request
        client = aiohttp_.AiohttpClient(aiohttp_session_mock)
        client._sync_callback_adapter = asyncio.coroutine
        request = aiohttp_.Request(client)

        # Run
        request.add_callback(lambda x: 2)
        response = request.send(1, 2, {})
        loop = asyncio.get_event_loop()
        value = loop.run_until_complete(asyncio.ensure_future(response))

        # Verify
        assert value == 2

    @requires_python34
    def test_threaded_callback(self, mocker):
        import asyncio

        def callback(response):
            return response

        # Mock response.
        response = mocker.Mock()
        response.text = asyncio.coroutine(mocker.stub())

        # Run
        new_callback = aiohttp_.threaded_callback(callback)
        return_value = new_callback(response)
        loop = asyncio.get_event_loop()
        value = loop.run_until_complete(asyncio.ensure_future(return_value))

        # Verify
        response.text.assert_called_with()
        assert value == response

    @requires_python34
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

    @requires_python34
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

    @requires_python34
    def test_create(self, mocker):
        # Setup
        import asyncio

        session_cls_mock = mocker.patch("aiohttp.ClientSession")
        positionals = [1]
        keywords = {"keyword": 2}

        # Run: Create client
        client = aiohttp_.AiohttpClient.create(*positionals, **keywords)

        # Verify: session hasn't been created yet.
        assert not session_cls_mock.called

        # Run: Get session
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.ensure_future(client.session()))

        # Verify: session created with args
        session_cls_mock.assert_called_with(*positionals, **keywords)
