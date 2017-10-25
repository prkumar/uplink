# Standard library imports
import collections

# Local imports
from uplink import backend


BackendFactory = collections.namedtuple(
    "BackendFactory", ("sync_backend", "async_backend")
)


class PreparedRequest(object):

    def __init__(self, backend_factory, request):
        self._backend = backend_factory
        self._request = request

    def execute(self):
        return self._backend.sync_backend.send_request(self._request)

    def enqueue(self):
        return self._backend.async_backend.send_request(self._request)


class Request(object):

    def __init__(self, client, args):
        self._args = iter(args)
        self._client = client

    def __enter__(self):
        args = tuple(self._args)
        self._client.audit_request(*args)
        return args

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self._client.handle_exception(exc_type, exc_val, exc_tb)

    def fulfill(self, response):
        return self._client.handle_response(response)


class BaseHttpClient(object):

    @property
    def _backend(self):  # pragma: no cover
        raise NotImplementedError

    def audit_request(self, method, url, extras):  # pragma: no cover
        pass

    def handle_exception(self, exc_type, exc_val, exc_tb):  # pragma: no cover
        pass

    def handle_response(self, response):
        return response

    def build_request(self, method, url, extras):
        request = Request(self, (method, url, extras))
        return PreparedRequest(self._backend, request)


class HttpClient(BaseHttpClient):

    def __init__(self):
        # TODO: Use DI instead of instantiation.
        self.__backend = BackendFactory(
            backend.RequestsBackend(),
            backend.AsyncioBackend()
        )

    @property
    def _backend(self):
        return self.__backend


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
    def _backend(self):
        return self._connection._backend

    def audit_request(self, method, url, extras):
        self._connection.audit_request(method, url, extras)

    def handle_exception(self, exc_type, exc_val, exc_tb):
        return self._connection.handle_exception(exc_type, exc_val, exc_tb)

    def handle_response(self, response):
        return self._connection.handle_response(response)

    def build_request(self, method, url, extras):
        return self._connection.build_request(method, url, extras)

