# Local imports
from uplink.clients import exceptions, io


class HttpClientAdapter(object):
    """An adapter of an HTTP client library."""

    __exceptions = exceptions.Exceptions()

    def create_request(self):
        raise NotImplementedError

    def io(self):
        """Returns the execution strategy for this client."""
        raise NotImplementedError

    @property
    def exceptions(self):
        """
        uplink.clients.exceptions.Exceptions: An enum of standard HTTP
        client errors that have been mapped to client specific
        exceptions.
        """
        return self.__exceptions

    def send(self, request, template, data):
        class Client(io.Client):
            def send(self, r):
                return request.send(*r)

        return io.execute(Client(), self.io(), template, data)


class Request(object):
    def send(self, method, url, extras):
        raise NotImplementedError

    def add_callback(self, callback):
        raise NotImplementedError

    def add_exception_handler(self, exception_handler):
        raise NotImplementedError
