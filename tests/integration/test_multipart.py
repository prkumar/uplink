# Local imports
from uplink import Consumer, PartMap, post, multipart

# Constants
BASE_URL = "https://example.com/"


def test_without_converter(mock_response, mock_client):
    class Calendar(Consumer):
        @multipart
        @post("/attachments", args={"files": PartMap})
        def upload_attachments(self, **files):
            pass

    mock_client.with_response(mock_response)
    calendar = Calendar(base_url=BASE_URL, client=mock_client)
    file = object()

    # Run
    calendar.upload_attachments(file=file)

    # Assertion: should not convert if converter is None
    request = mock_client.history[0]
    assert request.files == {"file": file}
