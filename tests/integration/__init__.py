# Local imports
from uplink import utils, clients
from uplink.clients import helpers, exceptions as client_exceptions


class MockClient(clients.interfaces.HttpClientAdapter):
    def __init__(self, request):
        self._mocked_request = request
        self._request = _HistoryMaintainingRequest(_MockRequest(request))
        self._exceptions = client_exceptions.Exceptions()

    def create_request(self):
        return self._request

    def with_response(self, response):
        self._mocked_request.send.return_value = response
        return self

    def with_side_effect(self, error):
        self._mocked_request.send.side_effect = error
        return self

    @property
    def exceptions(self):
        return self._exceptions

    @property
    def history(self):
        return self._request.history


class MockResponse(object):
    def __init__(self, response):
        self._response = response

    def with_json(self, json):
        self._response.json.return_value = json
        return self

    def __getattr__(self, item):
        return self._response.__getattr__(item)


class RequestInvocation(object):
    def __init__(self, method, url, extras):
        self._method = method
        self._url = url
        self._extras = extras

    @staticmethod
    def _get_endpoint(url):
        parsed_url = utils.urlparse.urlparse(url)
        return parsed_url.path

    @staticmethod
    def _get_base_url(url):
        parsed_url = utils.urlparse.urlparse(url)
        return utils.urlparse.urlunsplit(
            [parsed_url.scheme, parsed_url.netloc, "", "", ""]
        )

    @property
    def base_url(self):
        return self._get_base_url(self._url)

    @property
    def endpoint(self):
        return self._get_endpoint(self._url)

    def has_base_url(self, base_url):
        return self.base_url == self._get_base_url(base_url)

    def has_endpoint(self, endpoint):
        return self.endpoint == self._get_endpoint(endpoint)

    @property
    def url(self):
        return self._url

    @property
    def method(self):
        return self._method

    @property
    def params(self):
        return self._extras.get("params", None)

    @property
    def headers(self):
        return self._extras.get("headers", None)

    @property
    def data(self):
        return self._extras.get("data", None)

    @property
    def json(self):
        return self._extras.get("json", None)

    def __getattr__(self, item):
        try:
            return self._extras[item]
        except KeyError:
            raise AttributeError(item)


class _HistoryMaintainingRequest(clients.interfaces.Request):
    def __init__(self, request):
        self._request = request
        self._history = []

    def send(self, method, url, extras):
        self._history.append(RequestInvocation(method, url, extras))
        return self._request.send(method, url, extras)

    def add_callback(self, callback):
        self._request.add_callback(callback)

    def add_exception_handler(self, exception_handler):
        self._request.add_exception_handler(exception_handler)

    @property
    def history(self):
        return self._history


class _MockRequest(helpers.ExceptionHandlerMixin, clients.interfaces.Request):
    def __init__(self, mock_request):
        self._callbacks = []
        self._mock_request = mock_request

    def send(self, method, url, extras):
        with self._exception_handler:
            response = self._mock_request.send(method, url, extras)
        for callback in self._callbacks:
            response = callback(response)
        return response

    def add_callback(self, callback):
        self._callbacks.append(callback)
