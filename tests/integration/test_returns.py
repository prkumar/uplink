# Standard library imports
import collections

# Local imports.
import uplink

# Constants
BASE_URL = "https://api.github.com/"

# Schemas
Repo = collections.namedtuple("Repo", "owner name")

# Converters


@uplink.loads.from_json(Repo)
def repo_loader(cls, json):
    return cls(**json)


@uplink.dumps.to_json(Repo)
def repo_dumper(_, repo):
    return {"owner": repo.owner, "name": repo.name}


# Service


class GitHub(uplink.Consumer):
    @uplink.returns.from_json(type=Repo)
    @uplink.get("/users/{user}/repos/{repo}")
    def get_repo(self, user, repo):
        pass

    @uplink.returns.from_json(type=uplink.types.List[Repo], key="data")
    @uplink.get("/users/{user}/repos")
    def get_repos(self, user):
        pass

    @uplink.json
    @uplink.post("/users/{user}/repos", args={"repo": uplink.Body(Repo)})
    def create_repo(self, user, repo):
        pass


# Tests


def test_returns_json_with_type(mock_client, mock_response):
    # Setup
    mock_response.with_json({"owner": "prkumar", "name": "uplink"})
    mock_client.with_response(mock_response)
    github = GitHub(
        base_url=BASE_URL, client=mock_client, converters=repo_loader
    )

    # Run
    repo = github.get_repo("prkumar", "uplink")

    # Verify
    assert Repo(owner="prkumar", name="uplink") == repo


def test_returns_json_with_list(mock_client, mock_response):
    # Setup
    mock_response.with_json(
        {
            "data": [
                {"owner": "prkumar", "name": "uplink"},
                {"owner": "prkumar", "name": "uplink-protobuf"},
            ],
            "errors": [],
        }
    )
    mock_client.with_response(mock_response)
    github = GitHub(
        base_url=BASE_URL, client=mock_client, converters=repo_loader
    )

    # Run
    repo = github.get_repos("prkumar")

    # Verify
    assert [
        Repo(owner="prkumar", name="uplink"),
        Repo(owner="prkumar", name="uplink-protobuf"),
    ] == repo


def test_post_json(mock_client):
    # Setup
    github = GitHub(
        base_url=BASE_URL, client=mock_client, converters=repo_dumper
    )
    github.create_repo("prkumar", Repo(owner="prkumar", name="uplink"))
    request = mock_client.history[0]
    assert request.json == {"owner": "prkumar", "name": "uplink"}
