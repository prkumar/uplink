# Standard library imports
import atexit

# Local imports
from uplink.clients import helpers, interfaces, register

# Third party imports
import requests


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
            response = self._session.request(
                method=method,
                url=url,
                **extras
            )
        if self._callback is not None:
            response = self._callback(response)
        return response

    def add_callback(self, callback):
        self._callback = callback
