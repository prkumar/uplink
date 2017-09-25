# Local imports
from uplink import backend


class PreparedRequest(object):
    def __init__(self, sender, *request_args):
        self._sender = sender
        self._request_args = request_args

    def __getitem__(self, item):
        return self._request_args[item]

    def copy(self):
        return PreparedRequest(
            self._sender,
            self._request_args,
        )

    def send(self):
        return self._sender(*self._request_args)


class BaseHttpClient(object):

    def __build_request_call(self, *args, **kwargs):
        def wrapper():
            return self._request_sender(*args, **kwargs)
        return wrapper

    def __make_request(self, method, url, extras):
        self.audit_request(method, url, extras)
        request = self.__build_request_call(method, url, extras)
        response = self.wrap_request(request)
        return self.handle_response(response)

    @property
    def _request_sender(self):  # pragma: no cover
        raise NotImplementedError

    def audit_request(self, method, url, extras):
        pass

    def wrap_request(self, request):
        return request()

    def handle_response(self, response):
        return response

    def build_request(self, method, url, extras):
        return PreparedRequest(self.__make_request, method, url, extras)


class HttpClient(BaseHttpClient):
    _backend = backend.RequestsBackend()

    @property
    def _request_sender(self):
        return self._backend.send_request


class HttpClientDecorator(BaseHttpClient):
    """
    Decorator pattern for runtime modification of an API client's
    behavior.
    """

    def __init__(self, connection):
        assert isinstance(connection, BaseHttpClient)
        self._connection = connection

    def __getattr__(self, item):  # pragma: no cover
        return getattr(self._connection, item)

    @property
    def _request_sender(self):
        return self._connection._request_sender

    def audit_request(self, method, url, extras):
        self._connection.audit_request(method, url, extras)

    def wrap_request(self, request):
        return self._connection.wrap_request(request)

    def handle_response(self, response):
        return self._connection.handle_response(response)
