# Third-party imports
import pytest
import pytest_twisted

# Local imports.
from uplink import get, Consumer, retry
from uplink.clients import io

# Constants
BASE_URL = "https://api.github.com/"


def backoff_once():
    yield 0.1


backoff_default = retry.backoff.exponential(multiplier=0.1, minimum=0.1)


class GitHub(Consumer):
    @retry(max_attempts=2, backoff=backoff_default)
    @get("/users/{user}")
    def get_user(self, user):
        pass

    @retry(max_attempts=3, backoff=backoff_once)
    @get("repos/{user}/{repo}/issues/{issue}")
    def get_issue(self, user, repo, issue):
        pass

    @retry(
        stop=retry.stop.after_attempt(3), on_exception=retry.CONNECTION_TIMEOUT
    )
    @get("repos/{user}/{repo}/project/{project}")
    def get_project(self, user, repo, project):
        pass

    @retry(when=retry.when.status_5xx(), backoff=backoff_default)
    @get("repos/{user}/{repo}/issues")
    def get_issues(self, user, repo):
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
        github.get_issue("prkumar", "uplink", "#1")

    # Verify
    assert len(mock_client.history) == 2


def test_retry_fail_with_client_exception(mock_client, mock_response):
    # Setup
    mock_response.with_json({"id": 123, "name": "prkumar"})
    mock_client.exceptions.ConnectionTimeout = type(
        "ConnectionTimeout", (Exception,), {}
    )
    CustomException = type("CustomException", (Exception,), {})
    mock_client.with_side_effect(
        [
            mock_client.exceptions.ConnectionTimeout,
            CustomException,
            mock_response,
        ]
    )
    github = GitHub(base_url=BASE_URL, client=mock_client)

    # Run
    with pytest.raises(CustomException):
        github.get_project("prkumar", "uplink", "1")

    # Verify
    assert len(mock_client.history) == 2


def test_retry_fail_because_of_wait(mock_client, mock_response):
    # Setup
    mock_response.with_json({"id": 123, "name": "prkumar"})
    mock_client.with_side_effect([Exception, Exception, mock_response])
    github = GitHub(base_url=BASE_URL, client=mock_client)

    # Run
    with pytest.raises(Exception):
        github.get_issue("prkumar", "uplink", "#1")

    # Verify
    assert len(mock_client.history) == 2


def test_retry_with_status_501(mock_client, mock_response):
    # Setup
    mock_response.status_code = 501
    mock_client.with_side_effect([mock_response, Exception])
    github = GitHub(base_url=BASE_URL, client=mock_client)

    # Run
    with pytest.raises(Exception):
        github.get_issues("prkumar", "uplink")

    # Verify
    assert len(mock_client.history) == 2


@pytest_twisted.inlineCallbacks
def test_retry_with_twisted(mock_client, mock_response):
    from twisted.internet import defer

    @defer.inlineCallbacks
    def return_response():
        yield
        defer.returnValue(mock_response)

    # Setup
    mock_response.with_json({"id": 123, "name": "prkumar"})
    mock_client.with_side_effect([Exception, return_response()])
    mock_client.with_io(io.TwistedStrategy())
    github = GitHub(base_url=BASE_URL, client=mock_client)

    # Run
    response = yield github.get_user("prkumar")

    assert len(mock_client.history) == 2
    assert response.json() == {"id": 123, "name": "prkumar"}


@pytest_twisted.inlineCallbacks
def test_retry_fail_with_twisted(mock_client, mock_response):
    from twisted.internet import defer

    @defer.inlineCallbacks
    def return_response():
        yield
        defer.returnValue(mock_response)

    # Setup
    CustomException = type("CustomException", (Exception,), {})
    mock_response.with_json({"id": 123, "name": "prkumar"})
    mock_client.with_side_effect(
        [Exception, CustomException, return_response()]
    )
    mock_client.with_io(io.TwistedStrategy())
    github = GitHub(base_url=BASE_URL, client=mock_client)

    # Run
    with pytest.raises(CustomException):
        yield github.get_user("prkumar")

    assert len(mock_client.history) == 2
