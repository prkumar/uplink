
class BackendFactory(object):

    def make_backend(self):
        raise NotImplementedError


class HttpClientAdapter(BackendFactory):
    """An adapter of an HTTP client library."""

    @property
    def is_synchronous(self):
        raise NotImplementedError

    def create_request(self):
        raise NotImplementedError

    def make_backend(self):
        return Backend(
            *([self, None] if self.is_synchronous else [None, self])
        )

    def __and__(self, other):
        if self.is_synchronous != other.is_synchronous:
            return Backend(
                *([self, other] if self.is_synchronous else [other, self])
            )
        # TODO: Incompatible adapters.
        raise Exception()

    def __add__(self, other):
        return self.__and__(other)


class Request(object):

    def send(self, method, url, extras):
        raise NotImplementedError

    def add_callback(self, callback):
        raise NotImplementedError


class RequestHandler(object):

    def fulfill(self, request):
        raise NotImplementedError


class Backend(BackendFactory):

    def __init__(self, sync_client, async_client):
        self._sync_client = sync_client
        self._async_client = async_client

    def send_synchronous_request(self, request_handler):
        return request_handler.fulfill(self._sync_client.create_request())

    def send_asynchronous_request(self, request_handler):
        return request_handler.fulfill(self._async_client.create_request())

    def make_backend(self):
        return self
