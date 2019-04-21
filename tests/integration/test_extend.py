# Third-party imports
import pytest

# Local imports
import uplink

# Constants
BASE_URL = "https://api.github.com"


class GitHubError(Exception):
    pass


@uplink.response_handler
def github_error(response):
    if "errors" in response.json():
        raise GitHubError()
    return response


@uplink.timeout(10)
class GitHubService(uplink.Consumer):
    @github_error
    @uplink.json
    @uplink.post("graphql", args=(uplink.Body,))
    def graphql(self, **body):
        pass

    @uplink.returns.json(member=("data", "repository"))
    @uplink.args(body=uplink.Body)
    @graphql
    def get_repository(self, **body):
        pass

    @uplink.returns.json(member=("data", "repository"))
    @graphql.extend("graphql2", args=(uplink.Body,))
    def get_repository2(self, **body):
        pass


def test_get_repository(mock_client, mock_response):
    data = {
        "query": """\
query {
    repository(owner: "prkumar", name: "uplink") {
        nameWithOwner
    }
}"""
    }
    result = {"data": {"repository": {"nameWithOwner": "prkumar/uplink"}}}
    mock_response.with_json(result)
    mock_client.with_response(mock_response)
    github = GitHubService(base_url=BASE_URL, client=mock_client)
    response = github.get_repository(**data)
    request = mock_client.history[0]
    assert request.method == "POST"
    assert request.base_url == BASE_URL
    assert request.endpoint == "/graphql"
    assert request.timeout == 10
    assert request.json == data
    assert response == result["data"]["repository"]


def test_get_repository2_failure(mock_client, mock_response):
    data = {
        "query": """\
query {
    repository(owner: "prkumar", name: "uplink") {
        nameWithOwner
    }
}"""
    }
    result = {
        "data": {"repository": None},
        "errors": [
            {
                "type": "NOT_FOUND",
                "path": ["repository"],
                "locations": [{"line": 7, "column": 3}],
                "message": "Could not resolve to a User with the username 'prkussmar'.",
            }
        ],
    }
    mock_response.with_json(result)
    mock_client.with_response(mock_response)
    github = GitHubService(base_url=BASE_URL, client=mock_client)
    with pytest.raises(GitHubError):
        github.get_repository2(**data)
    request = mock_client.history[0]
    assert request.method == "POST"
    assert request.base_url == BASE_URL
    assert request.endpoint == "/graphql2"
    assert request.timeout == 10
