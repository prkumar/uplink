# Local imports
from uplink.clients.io import interfaces


class _BaseState(interfaces.RequestState):
    def __init__(self, request):
        self._request = request

    def send(self, request):
        return SendRequest(request)

    def fail(self, exc_type, exc_val, exc_tb):
        # Terminal
        return Fail(self._request, exc_type, exc_val, exc_tb)

    def finish(self, response):
        # Terminal
        return Finish(self._request, response)

    def sleep(self, duration):
        return SleepState(self._request, duration)

    def execute(self, context):
        raise NotImplementedError

    @property
    def request(self):
        return self._request


class BeforeRequest(_BaseState):
    def execute(self, context):
        return context.before_request(self._request)


class SleepState(interfaces.RequestState):
    class _Callback(interfaces.SleepCallback):
        def __init__(self, context, request):
            self._context = context
            self._request = request

        def on_success(self):
            self._context.state = BeforeRequest(self._request)
            return self._context.execute()

        def on_failure(self, exc_type, exc_val, exc_tb):
            self._context.state = AfterException(
                self._request, exc_type, exc_val, exc_tb
            )
            return self._context.execute()

    def __init__(self, request, duration):
        self._request = request
        self._duration = duration

    def execute(self, context):
        return context.sleep(
            self._duration, self._Callback(context, self._request)
        )

    @property
    def request(self):
        return self._request


class SendRequest(interfaces.RequestState):
    def __init__(self, request):
        self._request = request

    class _Callback(interfaces.SendCallback):
        def __init__(self, context, request):
            self._context = context
            self._request = request

        def on_success(self, response):
            self._context.state = AfterResponse(self._request, response)
            return self._context.execute()

        def on_failure(self, exc_type, exc_val, exc_tb):
            self._context.state = AfterException(
                self._request, exc_type, exc_val, exc_tb
            )
            return self._context.execute()

    def execute(self, context):
        return context.send(
            self._request, self._Callback(context, self._request)
        )

    @property
    def request(self):
        return self._request


class BaseAfterRequest(SendRequest):
    def prepare(self, request):
        return BeforeRequest(request)


class AfterResponse(BaseAfterRequest):
    def __init__(self, request, response):
        super(AfterResponse, self).__init__(request)
        self._response = response

    def execute(self, context):
        return context.after_response(self._request, self._response)


class AfterException(BaseAfterRequest):
    def __init__(self, request, exc_type, exc_val, exc_tb):
        super(AfterException, self).__init__(request)
        self._exc_type = exc_type
        self._exc_val = exc_val
        self._exc_tb = exc_tb

    def execute(self, context):
        return context.after_exception(
            self._request, self._exc_type, self._exc_val, self._exc_tb
        )


class TerminalState(interfaces.RequestState):
    def __init__(self, request):
        self._request = request

    @property
    def request(self):
        return self._request

    def execute(self, context):
        raise NotImplementedError


class Fail(TerminalState):
    def __init__(self, request, exc_type, exc_val, exc_tb):
        super(Fail, self).__init__(request)
        self._exc_type = exc_type
        self._exc_val = exc_val
        self._exc_tb = exc_tb

    def execute(self, context):
        return context.fail(self._exc_type, self._exc_val, self._exc_tb)


class Finish(TerminalState):
    def __init__(self, request, response):
        super(Finish, self).__init__(request)
        self._response = response

    def execute(self, context):
        return context.finish(self._response)
