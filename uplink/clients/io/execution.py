# Local imports
from uplink.clients.io import interfaces
from uplink.clients.io import state

__all__ = ["DefaultRequestExecution"]


class DefaultRequestExecution(interfaces.RequestExecution):
    def __init__(self, client, io, template, request):
        self._client = client
        self._template = template
        self._io = io
        self._state = state.BeforeRequest(request)

    def before_request(self, request):
        action = self._template.before_request(request)
        next_state = action(self._state)
        self._state = next_state
        return self.execute()

    def after_response(self, request, response):
        action = self._template.after_response(request, response)
        next_state = action(self._state)
        self._state = next_state
        return self.execute()

    def after_exception(self, request, exc_type, exc_val, exc_tb):
        action = self._template.after_exception(
            request, exc_type, exc_val, exc_tb
        )
        next_state = action(self._state)
        self._state = next_state
        return self.execute()

    def send(self, request, callback):
        return self._io.send(self._client, request, callback)

    def sleep(self, duration, callback):
        return self._io.sleep(duration, callback)

    def finish(self, response):
        return self._io.finish(response)

    def fail(self, exc_type, exc_val, exc_tb):
        return self._io.fail(exc_type, exc_val, exc_tb)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state

    def execute(self):
        return self.state.execute(self)
