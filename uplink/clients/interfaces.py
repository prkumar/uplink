
class HttpClientAdapter(object):
    """An adapter of an HTTP client library."""

    def create_request(self):
        raise NotImplementedError


class Request(object):

    def send(self, method, url, extras):
        raise NotImplementedError

    def add_callback(self, callback):
        raise NotImplementedError

    # TODO: Consider renaming this to `add_exception_handler`
    def add_error_handler(self, error_handler):
        raise NotImplementedError
