# Local imports.
import uplink

# Constants
BASE_URL = "https://example.com/"


@uplink.response_handler
def flag_consumer(consumer, response):
    consumer.flagged = True
    return response


@uplink.response_handler
def flag_response(response):
    response.flagged = True
    return response


class Calendar(uplink.Consumer):
    @flag_consumer
    @uplink.get("/todo/{todo_id}")
    def get_todo(self, todo_id):
        pass

    @flag_response
    @uplink.get("/month/{name}")
    def get_month(self, name):
        pass


def test_response_handler_with_consumer(mock_client):
    calendar = Calendar(base_url=BASE_URL, client=mock_client)
    calendar.flagged = False

    # Run
    calendar.get_todo(todo_id=1)

    # Verify
    assert calendar.flagged is True


def test_response_handler_with_response(mock_client):
    calendar = Calendar(base_url=BASE_URL, client=mock_client)

    # Run
    response = calendar.get_month("September")

    # Verify
    assert response.flagged is True
