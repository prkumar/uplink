# Third-party imports.
import pytest

# Local imports.
import uplink
from uplink.ratelimit import RateLimitExceeded, now

# Constants
BASE_URL = "https://api.github.com/"
DIFFERENT_BASE_URL = "https://hostedgithub.com/"


class CustomRateLimitException(RuntimeError):
    pass


class GitHub(uplink.Consumer):
    @uplink.ratelimit(
        calls=1, period=10, raise_on_limit=True, group_by=None
    )  # 1 call every 10 seconds
    @uplink.get("users/{user}")
    def get_user(self, user):
        pass

    @uplink.ratelimit(calls=1, period=1, raise_on_limit=False)
    @uplink.get("repos/{user}/{repo}")
    def get_repo(self, user, repo):
        pass

    @uplink.ratelimit(
        calls=1, period=10, raise_on_limit=CustomRateLimitException
    )
    @uplink.get("repos/{user}/{repo}/comments/{comment}")
    def get_comment(self, user, repo, comment):
        pass

    @uplink.ratelimit(calls=1, period=10, raise_on_limit=True, group_by=None)
    @uplink.get("repos/{user}/{repo}/issues")
    def get_issues(self, user, repo):
        pass

    @uplink.ratelimit(calls=1, period=10, raise_on_limit=True)
    @uplink.get("repos/{user}/{repo}/issues/{issue}")
    def get_issue(self, user, repo, issue):
        pass


# Tests


def test_limit_exceeded_by_1(mock_client):
    # Setup
    github = GitHub(base_url=BASE_URL, client=mock_client)

    # Run
    github.get_user("prkumar")

    with pytest.raises(RateLimitExceeded):
        github.get_user("prkumar")


def test_limit_exceeded_by_1_with_custom_exception(mock_client):
    # Setup
    github = GitHub(base_url=BASE_URL, client=mock_client)

    # Run
    github.get_comment("prkumar", "uplink", "1")

    with pytest.raises(CustomRateLimitException):
        github.get_comment("prkumar", "uplink", "1")


def test_exceeded_limit_wait(mock_client):
    # Setup
    github = GitHub(base_url=BASE_URL, client=mock_client)

    # Run
    start = now()
    github.get_repo("prkumar", "uplink")
    github.get_repo("prkumar", "uplink")
    elapsed = now() - start

    assert elapsed >= 1


def test_limit_with_group_by_None(mock_client):
    # Setup: consumers pointing to separate hosts
    github1 = GitHub(base_url=BASE_URL, client=mock_client)
    github2 = GitHub(base_url=DIFFERENT_BASE_URL, client=mock_client)

    # Run
    github1.get_issues("prkumar", "uplink")

    # Verify: the rate limit should be applied globally for all instances
    with pytest.raises(RateLimitExceeded):
        github2.get_issues("prkumar", "uplink")


def test_limit_with_group_by_host_and_port(mock_client):
    # Setup: consumers pointing to separate hosts
    github1 = GitHub(base_url=BASE_URL, client=mock_client)
    github2 = GitHub(base_url=DIFFERENT_BASE_URL, client=mock_client)

    # Run
    github1.get_issue("prkumar", "uplink", "issue1")

    # Verify: the rate limit should be applied separately by host-port,
    # so this request should be fine.
    github2.get_issue("prkumar", "uplink", "issue2")
