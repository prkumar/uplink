# Local imports
from uplink import compat
from uplink.clients.exceptions import ClientException


class ExceptionHandler(object):

    def __init__(self, exception_class=Exception):
        self._exc_cls = exception_class
        self._handler = None

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        et, ev = ClientException.wrap_exception_if_necessary(exc_type, exc_val)
        self.handle(et, ev, exc_tb)
        if (et, ev) != (exc_type, exc_val):
            # rethrow if we've wrapped the exception
            compat.reraise(et, ev, exc_tb)

    def set_handler(self, handler):
        self._handler = handler

    def handle(self, exc_type, exc_val, exc_tb):
        if self._handler is not None and isinstance(exc_val, self._exc_cls):
            self._handler(exc_type, exc_val, exc_tb)


class ExceptionHandlerMixin(object):
    __exception_handler = None

    @property
    def _exception_handler(self):
        if self.__exception_handler is None:
            self.__exception_handler = ExceptionHandler()
        return self.__exception_handler

    def add_exception_handler(self, exception_handler):
        self._exception_handler.set_handler(exception_handler)
