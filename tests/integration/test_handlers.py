# Local imports.
import uplink

# Constants
BASE_URL = "https://example.com/"


@uplink.response_handler(requires_consumer=True)
def handle_response_with_consumer(consumer, response):
    consumer.flagged = True
    return response


@uplink.response_handler
def handle_response(response):
    response.flagged = True
    return response


class WrappedException(Exception):
    def __init__(self, exception):
        self.exception = exception


@uplink.error_handler(requires_consumer=True)
def handle_error_with_consumer(consumer, exc_type, exc_value, exc_tb):
    consumer.flagged = True
    raise WrappedException(exc_value)


@uplink.error_handler
def handle_error(exc_type, exc_value, exc_tb):
    raise WrappedException(exc_value)


class Calendar(uplink.Consumer):
    @handle_response_with_consumer
    @uplink.get("todos/{todo_id}")
    def get_todo(self, todo_id):
        pass

    @handle_response
    @uplink.get("months/{name}/todos")
    def get_month(self, name):
        pass

    @handle_response_with_consumer
    @handle_response
    @uplink.get("months/{month}/days/{day}/todos")
    def get_day(self, month, day):
        pass

    @handle_error_with_consumer
    @uplink.get("users/{user_id}")
    def get_user(self, user_id):
        pass

    @handle_error
    @uplink.get("events/{event_id}")
    def get_event(self, event_id):
        pass


@handle_response
class CalendarV2(uplink.Consumer):
    @uplink.get("todos/{todo_id}")
    def get_todo(self, todo_id):
        pass


def test_class_response_handler(mock_client):
    calendar = CalendarV2(base_url=BASE_URL, client=mock_client)
    calendar.flagged = False

    # Run
    response = calendar.get_todo(todo_id=1)

    # Verify
    assert response.flagged is True


def test_response_handler_with_consumer(mock_client):
    calendar = Calendar(base_url=BASE_URL, client=mock_client)
    calendar.flagged = False

    # Run
    calendar.get_todo(todo_id=1)

    # Verify
    assert calendar.flagged is True


def test_response_handler(mock_client):
    calendar = Calendar(base_url=BASE_URL, client=mock_client)

    # Run
    response = calendar.get_month("September")

    # Verify
    assert response.flagged is True


def test_multiple_response_handlers(mock_client):
    calendar = Calendar(base_url=BASE_URL, client=mock_client)

    # Run
    response = calendar.get_day("September", 2)

    # Verify
    assert response.flagged
    assert calendar.flagged


def test_error_handler_with_consumer(mock_client):
    # Setup: raise specific exception
    expected_error = IOError()
    mock_client.with_side_effect(expected_error)

    calendar = Calendar(base_url=BASE_URL, client=mock_client)
    calendar.flagged = False

    # Run
    try:
        calendar.get_user(user_id=1)
    except WrappedException as err:
        assert err.exception == expected_error
        assert calendar.flagged is True
    else:
        raise AssertionError


def test_error_handler(mock_client):
    # Setup: raise specific exception
    expected_error = IOError()
    mock_client.with_side_effect(expected_error)

    calendar = Calendar(base_url=BASE_URL, client=mock_client)

    # Run
    try:
        calendar.get_event(event_id=1)
    except WrappedException as err:
        assert err.exception == expected_error
    else:
        raise AssertionError
