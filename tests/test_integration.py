# Third party imports
import pytest

# Local imports.
import uplink
from uplink import utils

# Constants
BASE_URL = "https://api.github.com/"


def _get_url(url):
    return utils.urlparse.urljoin(BASE_URL, url)


@uplink.headers({"Accept": "application/vnd.github.v3.full+json"})
class GitHubService(uplink.Consumer):

    @uplink.get("/users/{user}/repos")
    def list_repos(self, user): pass


@pytest.fixture
def github_service_and_client(http_client_mock):
    return (
        GitHubService(base_url=BASE_URL, client=http_client_mock),
        http_client_mock
    )


def test_list_repo(github_service_and_client):
    service, http_client = github_service_and_client
    service.list_repos("prkumar")
    http_client.create_request().send.assert_called_with(
        "GET", _get_url("/users/prkumar/repos"), {
            "headers": {
                "Accept": "application/vnd.github.v3.full+json"
            }
        }
    )

