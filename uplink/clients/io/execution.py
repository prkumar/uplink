# Local imports
from uplink.clients.io import interfaces
from uplink.clients.io import state

__all__ = ["RequestExecutionBuilder"]


class RequestExecutionBuilder(object):
    def __init__(self):
        self._client = None
        self._template = None
        self._io = None
        self._callbacks = []
        self._errbacks = []

    def with_client(self, client):
        self._client = client
        return self

    def with_template(self, template):
        self._template = template
        return self

    def with_io(self, io):
        self._io = io
        return self

    def with_callbacks(self, *callbacks):
        self._callbacks.extend(callbacks)
        return self

    def with_errbacks(self, *errbacks):
        self._errbacks.extend(errbacks)
        return self

    def build(self):
        execution = DefaultRequestExecution(
            self._client, self._io, self._template
        )
        for callback in self._callbacks:
            execution = CallbackDecorator(execution, self._io, callback)
        for errback in self._errbacks:
            execution = ErrbackDecorator(execution, self._io, errback)
        return execution


class DefaultRequestExecution(interfaces.RequestExecution):
    def __init__(self, client, io, template):
        self._client = client
        self._template = template
        self._io = io
        self._state = None

    def before_request(self, request):
        action = self._template.before_request(request)
        next_state = action(self._state)
        self._state = next_state
        return self.next()

    def after_response(self, request, response):
        action = self._template.after_response(request, response)
        next_state = action(self._state)
        self._state = next_state
        return self.next()

    def after_exception(self, request, exc_type, exc_val, exc_tb):
        action = self._template.after_exception(
            request, exc_type, exc_val, exc_tb
        )
        next_state = action(self._state)
        self._state = next_state
        return self.next()

    def send(self, request, callback):
        return self._io.invoke(self._client.send, (request,), {}, callback)

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

    def next(self):
        return self.state.execute(self)

    def execute(self, request):
        self._state = state.BeforeRequest(request)  # Start state
        return self._io.execute(self)


class RequestExecutionDecorator(interfaces.RequestExecution):
    def __init__(self, execution):
        self._execution = execution

    def before_request(self, request):
        return self._execution.before_request(request)

    def after_response(self, request, response):
        return self._execution.after_response(request)

    def after_exception(self, request, exc_type, exc_val, exc_tb):
        return self._execution.after_exception(
            request, exc_type, exc_val, exc_tb
        )

    def send(self, request, callback):
        return self._execution.send(request, callback)

    def sleep(self, duration, callback):
        return self._execution.sleep(duration, callback)

    def finish(self, response):
        return self._execution.finish(response)

    def fail(self, exc_type, exc_val, exc_tb):
        return self._execution.fail(exc_type, exc_val, exc_tb)

    @property
    def state(self):
        return self._execution.state

    @state.setter
    def state(self, new_state):
        self._execution.state = new_state

    def next(self):
        return self._execution.next()

    def execute(self, request):
        return self._execution.execute(request)


class FinishingCallback(interfaces.InvokeCallback):
    def __init__(self, execution):
        self._execution = execution

    def on_success(self, result):
        return self._execution.finish(result)

    def on_failure(self, exc_type, exc_val, exc_tb):
        raise self._execution.fail(exc_type, exc_val, exc_tb)


class FinishingDecorator(RequestExecutionDecorator):
    def __init__(self, execution, io):
        super(FinishingDecorator, self).__init__(execution)
        self._io = io

    def _invoke(self, func, *args, **kwargs):
        return self._io.invoke(
            func, args, kwargs, FinishingCallback(self._execution)
        )


class CallbackDecorator(FinishingDecorator):
    def __init__(self, execution, io, callback):
        super(CallbackDecorator, self).__init__(execution, io)
        self._callback = callback

    def finish(self, response):
        return self._invoke(self._callback, response)


class ErrbackDecorator(FinishingDecorator):
    def __init__(self, execution, io, errback):
        super(ErrbackDecorator, self).__init__(execution, io)
        self._errback = errback

    def fail(self, exc_type, exc_val, exc_tb):
        return self._invoke(self._errback, exc_type, exc_val, exc_tb)
