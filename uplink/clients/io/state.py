# Local imports
from uplink.clients.io import interfaces


class _BaseState(interfaces.RequestState):
    def __init__(self, request):
        self._request = request

    def send(self, executor, request):
        executor.state = SendRequest(request)

    def fail(self, executor, exc_type, exc_val, exc_tb):
        # Terminal
        executor.state = Fail(self._request, exc_type, exc_val, exc_tb)

    def finish(self, executor, response):
        # Terminal
        executor.state = Finish(self._request, response)

    def wait(self, executor, duration):
        executor.state = WaitState(self._request, duration)

    def execute(self, executor):
        raise NotImplementedError

    @property
    def request(self):
        return self._request


class BeforeRequest(_BaseState):
    def execute(self, executor):
        return executor.before_request(self._request)


class WaitState(interfaces.RequestState):
    class _Callback(interfaces.WaitCallback):
        def __init__(self, executor, request):
            self._executor = executor
            self._request = request

        def on_success(self):
            self._executor.state = BeforeRequest(self._request)
            return self._executor.execute()

        def on_failure(self, exc_type, exc_val, exc_tb):
            self._executor.state = AfterException(
                self._request, exc_type, exc_val, exc_tb
            )
            return self._executor.execute()

    def __init__(self, request, duration):
        self._request = request
        self._duration = duration

    def execute(self, executor):
        return executor.wait(
            self._duration, self._Callback(executor, self._request)
        )

    @property
    def request(self):
        return self._request


class SendRequest(interfaces.RequestState):
    def __init__(self, request):
        self._request = request

    class _Callback(interfaces.SendCallback):
        def __init__(self, executor, request):
            self._executor = executor
            self._request = request

        def on_success(self, response):
            self._executor.state = AfterResponse(self._request, response)
            return self._executor.execute()

        def on_failure(self, exc_type, exc_val, exc_tb):
            self._executor.state = AfterException(
                self._request, exc_type, exc_val, exc_tb
            )
            return self._executor.execute()

    def execute(self, executor):
        return executor.send(
            self._request, self._Callback(executor, self._request)
        )

    @property
    def request(self):
        return self._request


class BaseAfterRequest(SendRequest):
    def prepare(self, executor, request):
        executor.state = BeforeRequest(request)


class AfterResponse(BaseAfterRequest):
    def __init__(self, request, response):
        super(AfterResponse, self).__init__(request)
        self._response = response

    def execute(self, executor):
        return executor.after_response(self._request, self._response)


class AfterException(BaseAfterRequest):
    def __init__(self, request, exc_type, exc_val, exc_tb):
        super(AfterException, self).__init__(request)
        self._exc_type = exc_type
        self._exc_val = exc_val
        self._exc_tb = exc_tb

    def execute(self, executor):
        return executor.after_exception(
            self._request, self._exc_type, self._exc_val, self._exc_tb
        )


class TerminalState(interfaces.RequestState):
    def __init__(self, request):
        self._request = request

    @property
    def request(self):
        return self._request

    def execute(self, handler, executor):
        raise NotImplementedError


class Fail(TerminalState):
    def __init__(self, request, exc_type, exc_val, exc_tb):
        super(Fail, self).__init__(request)
        self._exc_type = exc_type
        self._exc_val = exc_val
        self._exc_tb = exc_tb

    def execute(self, executor):
        return executor.fail(self._exc_type, self._exc_val, self._exc_tb)


class Finish(TerminalState):
    def __init__(self, request, response):
        super(Finish, self).__init__(request)
        self._response = response

    def execute(self, executor):
        return executor.finish(self._response)
