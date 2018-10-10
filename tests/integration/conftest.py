# Third party imports
import pytest
import requests

# Local imports
from uplink import clients
from tests.integration import MockClient, MockResponse


@pytest.fixture
def mock_client(mocker):
    request = mocker.Mock(spec=clients.interfaces.Request)
    return MockClient(request)


@pytest.fixture
def mock_response(mocker):
    response = mocker.Mock(spec=requests.Response)
    return MockResponse(response)
