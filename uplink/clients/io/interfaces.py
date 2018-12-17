# Standard library imports
import collections


class UnsupportedRequestStateTransition(Exception):
    pass


class SendCallback(object):
    def on_success(self, response):
        raise NotImplementedError

    def on_failure(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError


class WaitCallback(object):
    def on_success(self):
        raise NotImplementedError

    def on_failure(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError


class Executable(collections.Iterator):
    def __next__(self):
        return self.execute()

    def execute(self):
        raise NotImplementedError


class RequestContext(Executable):
    @property
    def state(self):
        raise NotImplementedError

    def send(self, request, callback):
        raise NotImplementedError

    def wait(self, duration, callback):
        raise NotImplementedError

    def finish(self, response):
        raise NotImplementedError

    def fail(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def before_request(self, request):
        raise NotImplementedError

    def after_response(self, request, response):
        raise NotImplementedError

    def after_exception(self, request, exc_type, exc_val, exc_tb):
        raise NotImplementedError


class RequestState(object):
    @property
    def request(self):
        raise NotImplementedError

    def send(self, context, request):
        raise UnsupportedRequestStateTransition()

    def prepare(self, context, request):
        raise UnsupportedRequestStateTransition()

    def wait(self, context, duration):
        raise UnsupportedRequestStateTransition()

    def finish(self, context, response):
        raise UnsupportedRequestStateTransition()

    def fail(self, context, exc_type, exc_val, exc_tb):
        raise UnsupportedRequestStateTransition()

    def execute(self, context):
        raise NotImplementedError


class RequestTemplate(object):
    def before_request(self, request):
        pass

    def after_response(self, request, response):
        pass

    def after_exception(self, request, exc_type, exc_val, exc_tb):
        pass


class ExecutionStrategy(object):
    def send(self, client, request, callback):
        raise NotImplementedError

    def wait(self, duration, callback):
        raise NotImplementedError

    def finish(self, response):
        raise NotImplementedError

    def fail(self, exc_type, exc_val, exc_tb):
        # TODO: Reraise properly
        raise exc_val

    def execute(self, executable):
        raise NotImplementedError
