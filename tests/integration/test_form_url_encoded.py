# Local imports
from uplink import Consumer, form_url_encoded, put, FieldMap

# Constants
BASE_URL = "https://example.com/"


def test_without_converter(mock_response, mock_client):
    class Calendar(Consumer):
        @form_url_encoded
        @put("/user/repos", args={"event_data": FieldMap})
        def add_event(self, **event_data):
            pass

    mock_client.with_response(mock_response)
    calendar = Calendar(base_url=BASE_URL, client=mock_client)

    # Run
    calendar.add_event(name="Weekly Stand-up", public=True)

    # Assertions: should not convert if converter is None
    request = mock_client.history[0]
    assert request.data == {"name": "Weekly Stand-up", "public": True}
