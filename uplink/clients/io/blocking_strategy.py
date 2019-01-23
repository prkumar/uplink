# Third-party imports
import time

# Local models
from uplink.clients.io import interfaces

__all__ = ["BlockingStrategy"]


class BlockingStrategy(interfaces.IOStrategy):
    """A blocking execution strategy."""

    def invoke(self, func, arg, kwargs, callback):
        try:
            response = func(*arg, **kwargs)
        except Exception as error:
            # TODO: retrieve traceback
            return callback.on_failure(type(error), error, None)
        else:
            return callback.on_success(response)

    def sleep(self, duration, callback):
        time.sleep(duration)
        return callback.on_success()

    def finish(self, response):
        return response

    def execute(self, executable):
        return executable.next()
