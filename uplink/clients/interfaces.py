
class HttpClientAdapter(object):
    """An adapter of an HTTP client library."""

    def create_request(self):
        raise NotImplementedError


class Request(object):

    def send(self, method, url, extras):
        raise NotImplementedError

    def add_callback(self, callback):
        raise NotImplementedError

    def add_exception_handler(self, exception_handler):
        raise NotImplementedError
