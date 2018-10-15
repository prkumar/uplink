# Local imports
from uplink.clients import exceptions


class HttpClientAdapter(object):
    """An adapter of an HTTP client library."""

    __exceptions = exceptions.Exceptions()

    def create_request(self):
        raise NotImplementedError

    @property
    def exceptions(self):
        """
        uplink.clients.exceptions.Exceptions: An enum of standard HTTP
        client errors that have been mapped to client specific
        exceptions.
        """
        return self.__exceptions


class Request(object):
    def send(self, method, url, extras):
        raise NotImplementedError

    def add_callback(self, callback):
        raise NotImplementedError

    def add_exception_handler(self, exception_handler):
        raise NotImplementedError
