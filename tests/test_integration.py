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
class GitHubService(object):

    @uplink.get("/users/{user}/repos")
    def list_repos(self, user): pass


@pytest.fixture
def builder(http_client_mock):
    builder_ = uplink.Builder(GitHubService)
    builder_.base_url = BASE_URL
    builder_.client = http_client_mock
    return builder_


def test_list_repo(builder):
    service = builder.build()
    service.list_repos("prkumar").execute()
    builder.client.audit_request.assert_called_with(
        "GET", _get_url("/users/prkumar/repos"), {
            "headers": {
                "Accept": "application/vnd.github.v3.full+json"
            }
        }
    )

