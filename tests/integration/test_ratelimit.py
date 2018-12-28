# Local imports.
import uplink
from uplink.ratelimit import now

# Constants
BASE_URL = "https://api.github.com/"


class GitHub(uplink.Consumer):
    @uplink.ratelimit(calls=1, period=1)
    @uplink.get("/users/{user}")
    def get_user(self, user):
        pass


# Tests


def test_limit_exceeded_by_1(mock_client):
    # Setup
    github = GitHub(base_url=BASE_URL, client=mock_client)

    # Run
    start_time = now()
    github.get_user("prkumar")
    github.get_user("prkumar")
    elapsed_time = now() - start_time

    # Verify
    assert elapsed_time >= 1


def test_exact_limit(mock_client):
    # Setup
    github = GitHub(base_url=BASE_URL, client=mock_client)

    # Run
    start_time = now()
    github.get_user("prkumar")
    elapsed_time = now() - start_time

    # Verify
    assert elapsed_time <= 1
