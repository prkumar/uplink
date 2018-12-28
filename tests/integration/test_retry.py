# Third-party imports
import pytest
import pytest_twisted

# Local imports.
import uplink
from uplink.clients import io
from tests import requires_python34

# Constants
BASE_URL = "https://api.github.com/"


def wait_once():
    yield 0.1


wait_default = uplink.retry.exponential_backoff(multiplier=0.1, minimum=0.1)


class GitHub(uplink.Consumer):
    @uplink.retry(max_attempts=2, wait=wait_default)
    @uplink.get("/users/{user}")
    def get_user(self, user):
        pass

    @uplink.retry(max_attempts=3, wait=wait_once)
    @uplink.get("/{user}/{repo}/{issue}")
    def get_issue(self, user, repo, issue):
        pass

    @uplink.retry(max_attempts=3, when_raises=uplink.retry.CONNECTION_TIMEOUT)
    @uplink.get("/{user}/{repo}/{project}")
    def get_project(self, user, repo, project):
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


@requires_python34
def test_retry_with_asyncio(mock_client, mock_response):
    import asyncio

    @asyncio.coroutine
    def coroutine():
        return mock_response

    # Setup
    mock_response.with_json({"id": 123, "name": "prkumar"})
    mock_client.with_side_effect([Exception, coroutine()])
    mock_client.with_io(io.AsyncioStrategy())
    github = GitHub(base_url=BASE_URL, client=mock_client)

    # Run
    awaitable = github.get_user("prkumar")
    loop = asyncio.get_event_loop()
    response = loop.run_until_complete(asyncio.ensure_future(awaitable))

    # Verify
    assert len(mock_client.history) == 2
    assert response.json() == {"id": 123, "name": "prkumar"}


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
