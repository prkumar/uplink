# Local imports.
import uplink

# Third-party imports
import aiohttp
import pytest
from uplink.clients.aiohttp_ import AiohttpClient

# Constants
BASE_URL = "https://example.com/"
SIMPLE_RESPONSE = "simple response"


@pytest.fixture
def mock_aiohttp_session(mocker):
    return mocker.Mock(spec=aiohttp.ClientSession)


@uplink.response_handler
async def simple_async_handler(response):
    return SIMPLE_RESPONSE


class Calendar(uplink.Consumer):
    @simple_async_handler
    @uplink.get("todos/{todo_id}")
    def get_todo(self, todo_id):
        pass


@pytest.mark.asyncio
async def test_simple_async_handler(mock_aiohttp_session, mock_response):
    mock_response.status = 200

    async def request(*args, **kwargs):
        return mock_response

    mock_aiohttp_session.request = request

    calendar = Calendar(
        base_url=BASE_URL, client=AiohttpClient(mock_aiohttp_session)
    )

    # Run
    response = await calendar.get_todo(todo_id=1)

    # Verify
    assert response == SIMPLE_RESPONSE
