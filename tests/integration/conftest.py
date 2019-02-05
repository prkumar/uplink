# Third-party imports
import pytest
import requests

# Local imports
from uplink import clients
from tests.integration import MockClient, MockResponse


@pytest.fixture
def mock_client(mocker):
    client = mocker.Mock(spec=clients.interfaces.HttpClientAdapter)
    return MockClient(client)


@pytest.fixture
def mock_response(mocker):
    response = mocker.Mock(spec=requests.Response)
    return MockResponse(response)
