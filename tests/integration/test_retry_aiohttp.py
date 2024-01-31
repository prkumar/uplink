# Third-party imports
import pytest

# Local imports.
from uplink.clients import io

from . import test_retry
import sys


@pytest.mark.asyncio
async def test_retry_with_asyncio(mock_client, mock_response):
    # Check the Python version and define coroutine accordingly
    if sys.version_info >= (3, 5):
        # For Python 3.5 and newer
        async def coroutine():
            return mock_response
    elif (3, 3) <= sys.version_info < (3, 5):
        # For Python 3.3 and 3.4
        import asyncio
        @asyncio.coroutine
        def coroutine():
            yield
            return mock_response
    else:
        # Not applicable for Python 2
        return

    mock_response.with_json({"id": 123, "name": "prkumar"})
    mock_client.with_side_effect([Exception, coroutine()])
    mock_client.with_io(io.AsyncioStrategy())
    github = test_retry.GitHub(base_url=test_retry.BASE_URL, client=mock_client)

    # Run
    response = await github.get_user("prkumar")

    # Verify
    assert len(mock_client.history) == 2
    assert response.json() == {"id": 123, "name": "prkumar"}
