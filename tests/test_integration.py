# Third party imports
import pytest

# Local imports.
import uplink
from uplink import utils
from uplink.builder import Consumer

# Constants
BASE_URL = "https://api.github.com/"


def _get_url(url):
    return utils.urlparse.urljoin(BASE_URL, url)


@uplink.headers({"Accept": "application/vnd.github.v3.full+json"})
class GitHubService(Consumer):

    @uplink.get("/users/{user}/repos")
    def list_repos(self, user): pass


@pytest.fixture
def github_service_and_client(http_client_mock):
    return GitHubService(base_url=BASE_URL, http_client=http_client_mock), http_client_mock

def test_list_repo(github_service_and_client):
    service, http_client_mock = github_service_and_client
    service.list_repos("prkumar").execute()
    http_client_mock.audit_request.assert_called_with(
        "GET", _get_url("/users/prkumar/repos"), {
            "headers": {
                "Accept": "application/vnd.github.v3.full+json"
            }
        }
    )

