
class Backend(object):
    """An adapter of an HTTP client library."""

    def send_request(self, request):
        raise NotImplementedError
