# Third-party imports
import pytest

# Local imports.
import uplink

# Constants
BASE_URL = "https://api.github.com/"


class GitHub(uplink.Consumer):
    @uplink.retry(max_attempts=2)
    @uplink.get("/users/{user}")
    def get_user(self, user):
        pass


# Tests


def test_retry(mock_client, mock_response):
    # Setup
    mock_response.with_json({"id": 123, "name": "prkumar"})
    mock_client.with_side_effect([Exception, mock_response])
    github = GitHub(base_url=BASE_URL, client=mock_client)

    # Run
    response = github.get_user("prkumar")

    # Verify
    assert len(mock_client.history) == 2
    assert response.json() == {"id": 123, "name": "prkumar"}


def test_retry_fail(mock_client, mock_response):
    # Setup
    mock_response.with_json({"id": 123, "name": "prkumar"})
    mock_client.with_side_effect([Exception, Exception, mock_response])
    github = GitHub(base_url=BASE_URL, client=mock_client)

    # Run
    with pytest.raises(Exception):
        github.get_user("prkumar")

    # Verify
    assert len(mock_client.history) == 2
