# Third party imports
import pytest
import requests

# Local imports.
import uplink
from uplink import utils, clients

# Constants
BASE_URL = "https://api.github.com/"


def _get_url(url):
    return utils.urlparse.urljoin(BASE_URL, url)


@uplink.timeout(10)
@uplink.headers({"Accept": "application/vnd.github.v3.full+json"})
class GitHubService(uplink.Consumer):
    @uplink.timeout(15)
    @uplink.get("/users/{user}/repos")
    def list_repos(self, user):
        pass

    @uplink.returns.json
    @uplink.get("/users/{user}/repos/{repo}")
    def get_repo(self, user, repo):
        pass


@pytest.fixture
def github_service_and_client(http_client_mock):
    return (
        GitHubService(base_url=BASE_URL, client=http_client_mock),
        http_client_mock,
    )


def test_list_repo(github_service_and_client):
    service, http_client = github_service_and_client
    service.list_repos("prkumar")
    http_client.create_request().send.assert_called_with(
        "GET",
        _get_url("/users/prkumar/repos"),
        {
            "headers": {"Accept": "application/vnd.github.v3.full+json"},
            "timeout": 15,
        },
    )


class RequestMock(clients.interfaces.Request):
    def __init__(self, response):
        self._response = response
        self._callback = None

    def send(self, method, url, extras):
        if self._callback is not None:
            return self._callback(self._response)
        else:
            return self._response

    def add_callback(self, callback):
        self._callback = callback

    def add_exception_handler(self, exception_handler):
        pass


def test_get_repo(github_service_and_client, mocker):
    """
    This integration test ensures that the returns.json returns the
    Json body when a model is not provided.
    """
    # Setup: return a mock response
    service, http_client = github_service_and_client
    response = mocker.Mock(spec=requests.Response)
    expected_body = response.json.return_value = {"key": "value"}
    http_client.create_request.return_value = RequestMock(response)

    # Run
    result = service.get_repo("prkumar", "uplink")

    # Verify
    assert expected_body == result
