# Standard library imports
import sys

# Third party imports
import pytest
import inspect

# Local imports
from uplink.clients import twisted_

try:
    from uplink.clients import aiohttp_
except (ImportError, SyntaxError):
    aiohttp_ = None


requires_aiohttp = pytest.mark.skipif(
    not aiohttp_, reason="Requires Python 3.4 or above")


class TestTwisted(object):

    def test_create_requests(self, http_client_mock):
        twisted = twisted_.TwistedClient(http_client_mock)
        request = twisted.create_request()
        assert request._proxy is http_client_mock.create_request()
        assert isinstance(request, twisted_.Request)

    def test_request_send(self, mocker,  request_mock):
        deferToThread = mocker.patch.object(twisted_.threads, "deferToThread")
        request = twisted_.Request(request_mock)
        request.send(1, 2, 3)
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
        request = aiohttp_.Request(aiohttp_session_mock)
        response = request.send(1, 2, {})
        assert inspect.isgenerator(response)
        assert list(response) == [0]

    @requires_aiohttp
    def test_callback(self, aiohttp_session_mock):
        aiohttp_session_mock.request.return_value = [0]
        request = aiohttp_.Request(aiohttp_session_mock)
        request.add_callback(lambda x: 2)
        response = request.send(1, 2, {})
        assert inspect.isgenerator(response)
        assert list(response) == [0]
        try:
            next(response)
        except StopIteration as err:
            err.value == 2
        else:
            assert False



