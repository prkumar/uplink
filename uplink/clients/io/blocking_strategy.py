# Third-party imports
import time

# Local models
from uplink.clients.io import interfaces

__all__ = ["BlockingStrategy"]


class BlockingStrategy(interfaces.IOStrategy):
    """A blocking execution strategy."""

    def send(self, client, request, callback):
        try:
            response = client.send(request)
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
        return executable.execute()
