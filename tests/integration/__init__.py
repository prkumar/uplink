# Local imports
from uplink import utils, clients
from uplink.clients import io, exceptions as client_exceptions


class MockClient(clients.interfaces.HttpClientAdapter):
    def __init__(self, mock_client):
        self._mock_client = mock_client
        self._exceptions = client_exceptions.Exceptions()
        self._history = []
        self._io = io.BlockingStrategy()

    def with_response(self, response):
        self._mock_client.send.return_value = response
        return self

    def with_side_effect(self, side_effect):
        self._mock_client.send.side_effect = side_effect
        return self

    @property
    def exceptions(self):
        return self._exceptions

    @property
    def history(self):
        return self._history

    def with_io(self, io_):
        self._io = io_
        return self

    def io(self):
        return self._io

    def apply_callback(self, callback, response):
        return callback(response)

    def send(self, request):
        method, url, extras = request
        self._history.append(RequestInvocation(method, url, extras))
        return self._mock_client.send(method, url, extras)


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
    def files(self):
        return self._extras.get("files", None)

    @property
    def json(self):
        return self._extras.get("json", None)

    def __getattr__(self, item):
        try:
            return self._extras[item]
        except KeyError:
            raise AttributeError(item)
