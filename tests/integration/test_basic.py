# Local imports.
import uplink

# Constants
BASE_URL = "https://api.github.com/"


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


def test_list_repo(mock_client):
    github = GitHubService(base_url=BASE_URL, client=mock_client)
    github.list_repos("prkumar")
    request = mock_client.history[0]
    assert request.method == "GET"
    assert request.has_base_url(BASE_URL)
    assert request.has_endpoint("/users/prkumar/repos")
    assert request.headers == {"Accept": "application/vnd.github.v3.full+json"}
    assert request.timeout == 15


def test_get_repo(mock_client, mock_response):
    """
    This integration test ensures that the returns.json returns the
    Json body when a model is not provided.
    """
    # Setup: return a mock response
    expected_json = {"key": "value"}
    mock_response.with_json(expected_json)
    mock_client.with_response(mock_response)
    github = GitHubService(base_url=BASE_URL, client=mock_client)

    # Run
    actual_json = github.get_repo("prkumar", "uplink")

    # Verify
    assert expected_json == actual_json
