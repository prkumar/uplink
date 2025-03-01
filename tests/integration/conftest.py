# Third-party imports
import pytest
import requests

from tests.integration import MockClient, MockResponse

# Local imports
from uplink import clients


@pytest.fixture
def mock_client(mocker):
    client = mocker.Mock(spec=clients.interfaces.HttpClientAdapter)
    return MockClient(client)


@pytest.fixture
def mock_response(mocker):
    response = mocker.Mock(spec=requests.Response)
    return MockResponse(response)
