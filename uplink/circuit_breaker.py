# Local imports
from uplink.clients.io import RequestTemplate, transitions


class CircuitBreaker(object):
    def report_success(self, response):
        raise NotImplementedError

    def report_failure(self, response):
        raise NotImplementedError

    def report_exception(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    def is_tripped(self):
        raise NotImplementedError


class FailureChecker(object):
    def is_failure(self, response):
        raise NotImplementedError

    def is_expected_exception(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError


class BasicFailureChecker(FailureChecker):
    def is_failure(self, response):
        return False

    def is_expected_exception(self, exc_type, exc_val, exc_tb):
        return False


class CircuitRequestTemplate(RequestTemplate):
    def __init__(self, circuit_breaker, fallback_func, failure_checker):
        self._circuit_breaker = circuit_breaker
        self._fallback_func = fallback_func
        self._failure_checker = failure_checker

    def before_request(self, request):
        if self._circuit_breaker.is_tripped():
            # Short-circuit.
            return transitions.finish(self._fallback_func(request))

    def after_response(self, request, response):
        if self._failure_checker.is_failure(response):
            self._circuit_breaker.report_failure(response)
            return transitions.finish(self._fallback_func(request))
        else:
            self._circuit_breaker.report_success(response)

    def after_exception(self, request, exc_type, exc_val, exc_tb):
        self._circuit_breaker.report_exception(exc_type, exc_val, exc_tb)
        if self._failure_checker.is_expected_exception(
            exc_type, exc_val, exc_tb
        ):
            return transitions.finish(self._fallback_func(request))
