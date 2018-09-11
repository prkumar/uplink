# Local imports
from uplink import session


def test_base_url(uplink_builder_mock):
    # Setup
    uplink_builder_mock.base_url = "https://api.github.com"
    sess = session.Session(uplink_builder_mock)

    # Run & Verify
    assert uplink_builder_mock.base_url == sess.base_url


def test_headers(uplink_builder_mock):
    # Setup
    sess = session.Session(uplink_builder_mock)

    # Run
    sess.headers["key"] = "value"

    # Verify
    assert uplink_builder_mock.add_hook.called
    assert sess.headers == {"key": "value"}


def test_params(uplink_builder_mock):
    # Setup
    sess = session.Session(uplink_builder_mock)

    # Run
    sess.params["key"] = "value"

    # Verify
    assert uplink_builder_mock.add_hook.called
    assert sess.params == {"key": "value"}


def test_auth(uplink_builder_mock):
    # Setup
    uplink_builder_mock.auth = ("username", "password")
    sess = session.Session(uplink_builder_mock)

    # Run & Verify
    assert uplink_builder_mock.auth == sess.auth


def test_auth_set(uplink_builder_mock):
    # Setup
    sess = session.Session(uplink_builder_mock)

    # Run
    sess.auth = ("username", "password")

    # Verify
    assert ("username", "password") == uplink_builder_mock.auth
