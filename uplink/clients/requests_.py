# Standard library imports
import atexit

# Third party imports
import requests

# Local imports
from uplink.clients import exceptions, helpers, interfaces, register


class RequestsClient(interfaces.HttpClientAdapter):
    """
    A :py:mod:`requests` client that returns
    :py:class:`requests.Response` responses.

    Args:
        session (:py:class:`requests.Session`, optional): The session
            that should handle sending requests. If this argument is
            omitted or set to :py:obj:`None`, a new session will be
            created.
    """

    exceptions = exceptions.Exceptions()

    def __init__(self, session=None, **kwargs):
        if session is None:
            session = self._create_session(**kwargs)
        self.__session = session

    def create_request(self):
        return Request(self.__session)

    @staticmethod
    @register.handler
    def with_session(session, *args, **kwargs):
        if isinstance(session, requests.Session):
            return RequestsClient(session, *args, **kwargs)

    @staticmethod
    def _create_session(**kwargs):
        session = requests.Session()
        atexit.register(session.close)
        for key in kwargs:
            setattr(session, key, kwargs[key])
        return session


class Request(helpers.ExceptionHandlerMixin, interfaces.Request):
    def __init__(self, session):
        self._session = session
        self._callback = None

    def send(self, method, url, extras):
        with self._exception_handler:
            response = self._session.request(method=method, url=url, **extras)
        if self._callback is not None:
            response = self._callback(response)
        return response

    def add_callback(self, callback):
        self._callback = callback


# === Register client exceptions === #
RequestsClient.exceptions.BaseClientException = requests.RequestException
RequestsClient.exceptions.ConnectionError = requests.ConnectionError
RequestsClient.exceptions.ConnectionTimeout = requests.ConnectTimeout
RequestsClient.exceptions.ServerTimeout = requests.ReadTimeout
RequestsClient.exceptions.SSLError = requests.exceptions.SSLError
RequestsClient.exceptions.InvalidURL = requests.exceptions.InvalidURL
