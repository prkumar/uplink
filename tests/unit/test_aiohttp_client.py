# Standard library imports
import contextlib

# Third-party imports
import aiohttp
import asyncio
import pytest

# Local imports
from uplink.clients import (
    AiohttpClient,
    aiohttp_,
    register,
    io,
)


@contextlib.contextmanager
def _patch(obj, attr, value):
    if obj is not None:
        old_value = getattr(obj, attr)
        setattr(obj, attr, value)
    yield
    if obj is not None:
        setattr(obj, attr, old_value)


@pytest.fixture
def aiohttp_session_mock(mocker):
    return mocker.Mock(spec=aiohttp.ClientSession)


class AsyncMock(object):
    def __init__(self, result=None):
        self._result = result
        self._calls = 0

    async def __call__(self, *args, **kwargs):
        self._calls += 1
        f = asyncio.Future()
        f.set_result(self._result)
        return f

    @property
    def called(self):
        return self._calls > 0


class TestAiohttp(object):
    def test_init_when_aiohttp_is_not_installed(self):
        with _patch(aiohttp_, "aiohttp", None):
            with pytest.raises(NotImplementedError):
                AiohttpClient()

    def test_init_with_session_None(self, mocker):
        mocker.spy(AiohttpClient, "_create_session")
        AiohttpClient(kwarg1="value")
        AiohttpClient._create_session.assert_called_with(kwarg1="value")

    def test_get_client(self, aiohttp_session_mock):
        client = register.get_client(aiohttp_session_mock)
        assert isinstance(client, aiohttp_.AiohttpClient)

    @pytest.mark.asyncio
    async def test_request_send(self, mocker, aiohttp_session_mock):
        # Setup
        expected_response = mocker.Mock()

        async def request(*args, **kwargs):
            return expected_response

        aiohttp_session_mock.request = request
        client = aiohttp_.AiohttpClient(aiohttp_session_mock)

        # Run
        response = await client.send((1, 2, {}))

        # Verify
        assert response == expected_response

    @pytest.mark.asyncio
    async def test_callback(self, mocker, aiohttp_session_mock):
        # Setup
        expected_response = mocker.Mock(spec=aiohttp_.aiohttp.ClientResponse)
        expected_response.text = AsyncMock()

        async def request(*args, **kwargs):
            return expected_response

        aiohttp_session_mock.request = request
        client = aiohttp_.AiohttpClient(aiohttp_session_mock)

        # Run
        async def call():
            response = await client.send((1, 2, {}))
            response = await client.apply_callback(lambda x: 2, response)
            return response

        value = await call()

        # Verify
        assert value == 2
        assert expected_response.text.called

    def test_wrap_callback(self, mocker):
        # Setup
        c = AiohttpClient()
        mocker.spy(c, "_sync_callback_adapter")

        # Run: with callback that is not a coroutine
        def callback(*_):
            pass

        c.wrap_callback(callback)

        # Verify: Should wrap it
        c._sync_callback_adapter.assert_called_with(callback)

        # Run: with coroutine callback
        async def awaitable_callback():
            pass

        assert c.wrap_callback(awaitable_callback) is awaitable_callback

    @pytest.mark.asyncio
    async def test_threaded_callback(self, mocker):
        def callback(response):
            return response

        # Mock response.
        response = mocker.Mock(spec=aiohttp_.aiohttp.ClientResponse)
        response.text = AsyncMock()

        # Run
        new_callback = aiohttp_.threaded_callback(callback)
        return_value = await new_callback(response)

        # Verify
        assert response.text.called
        assert return_value == response

        # Run: Verify with callback that returns new value
        def callback(*_):
            return 1

        new_callback = aiohttp_.threaded_callback(callback)
        value = await new_callback(response)
        assert value == 1
        assert response.text.called

        # Run: Verify with response that is not ClientResponse (should not be wrapped)
        response = mocker.Mock()
        await new_callback(response)
        assert not response.text.called

    def test_threaded_coroutine(self):
        async def coroutine():
            return 1

        threaded_coroutine = aiohttp_.ThreadedCoroutine(coroutine)

        # Run -- should block
        response = threaded_coroutine()

        # Verify
        assert response == 1

    def test_threaded_response(self, mocker):
        async def coroutine():
            return 1

        def not_a_coroutine():
            return 2

        response = mocker.Mock()
        response.coroutine = coroutine
        response.not_coroutine = not_a_coroutine
        threaded_response = aiohttp_.ThreadedResponse(response)

        # Run
        threaded_coroutine = threaded_response.coroutine
        return_value = threaded_coroutine()

        # Verify
        assert isinstance(threaded_coroutine, aiohttp_.ThreadedCoroutine)
        assert return_value == 1
        assert threaded_response.not_coroutine is not_a_coroutine

    @pytest.mark.asyncio
    async def test_create(self, mocker):
        session_cls_mock = mocker.patch("aiohttp.ClientSession")
        positionals = [1]
        keywords = {"keyword": 2}

        # Run: Create client
        client = aiohttp_.AiohttpClient.create(*positionals, **keywords)

        # Verify: session hasn't been created yet.
        assert not session_cls_mock.called

        # Run: Get session
        await client.session()

        # Verify: session created with args
        session_cls_mock.assert_called_with(*positionals, **keywords)

    @pytest.mark.asyncio
    async def test_close_auto_created_session(self, mocker):
        # Setup
        import gc

        mock_session = mocker.Mock(spec=aiohttp.ClientSession)
        session_cls_mock = mocker.patch("aiohttp.ClientSession")
        session_cls_mock.return_value = mock_session

        positionals = [1]
        keywords = {"keyword": 2}

        # Run: Create client
        client = aiohttp_.AiohttpClient.create(*positionals, **keywords)

        # Run: Get session
        await client.session()

        # Verify: session created with args
        session_cls_mock.assert_called_with(*positionals, **keywords)

        # Verify: session closed on garbage collection
        del client
        gc.collect()
        session_cls_mock.return_value.close.assert_called_with()

    def test_exceptions(self):
        import aiohttp

        exceptions = aiohttp_.AiohttpClient.exceptions

        with pytest.raises(exceptions.BaseClientException):
            raise aiohttp.ClientError()

        with pytest.raises(exceptions.BaseClientException):
            # Test polymorphism
            raise aiohttp.InvalidURL("invalid")

        with pytest.raises(exceptions.ConnectionError):
            raise aiohttp.ClientConnectionError()

        with pytest.raises(exceptions.ConnectionTimeout):
            raise aiohttp.ClientConnectorError.__new__(
                aiohttp.ClientConnectorError
            )

        with pytest.raises(exceptions.ServerTimeout):
            raise aiohttp.ServerTimeoutError()

        with pytest.raises(exceptions.SSLError):
            raise aiohttp.ClientSSLError.__new__(aiohttp.ClientSSLError)

        with pytest.raises(exceptions.InvalidURL):
            raise aiohttp.InvalidURL("invalid")

    def test_io(self):
        assert isinstance(aiohttp_.AiohttpClient.io(), io.AsyncioStrategy)
