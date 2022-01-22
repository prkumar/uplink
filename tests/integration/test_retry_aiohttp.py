# Third-party imports
import pytest

# Local imports.
from uplink.clients import io

from . import test_retry


@pytest.mark.asyncio
async def test_retry_with_asyncio(mock_client, mock_response):
    import asyncio

    @asyncio.coroutine
    def coroutine():
        return mock_response

    # Setup
    mock_response.with_json({"id": 123, "name": "prkumar"})
    mock_client.with_side_effect([Exception, coroutine()])
    mock_client.with_io(io.AsyncioStrategy())
    github = test_retry.GitHub(base_url=test_retry.BASE_URL, client=mock_client)

    # Run
    response = await github.get_user("prkumar")

    # Verify
    assert len(mock_client.history) == 2
    assert response.json() == {"id": 123, "name": "prkumar"}
