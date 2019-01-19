# Standard library imports
import contextlib
import threading

# Local imports
from uplink.clients.io import RequestTemplate, transitions


class FailureTracker(object):
    _failures = 0

    def __init__(self, max_failures, circuit_breaker):
        self._max_failures = max_failures
        self._circuit_breaker = circuit_breaker
        self.__lock = threading.RLock()
        self._failures = 0

    def increment(self):
        with self._acquire_lock():
            self._failures = min(self._failures + 1, self._max_failures)
            if self._failures > self._max_failures:
                self._circuit_breaker.trip()

    def decrement(self):
        with self._acquire_lock():
            self._decrement_without_lock(1)

    def _decrement_without_lock(self, delta):
        self._failures = max(self._failures - delta, 0)
        if (
            self._circuit_breaker.tripped()
            and self._failures <= self._max_failures
        ):
            self._circuit_breaker.reset()

    @contextlib.contextmanager
    def _acquire_lock(self):
        with self.__lock:
            since_last_reset = self._clock() - self._last_reset
            if since_last_reset >= self._period:
                self.__decrement_without_lock(since_last_reset / self._period)
                self._last_reset = self._clock()
            yield


class CircuitBreaker(object):
    def __init__(self):
        self._tripped = False
        self._force_tripped = False
        self._lock = threading.RLock()

    def trip(self):
        with self._lock:
            self._tripped = True

    def reset(self):
        with self._lock:
            self._tripped = False

    def force_trip(self):
        with self._lock:
            self._force_tripped = True

    def force_reset(self):
        with self._lock:
            self._force_tripped = False

    @property
    def tripped(self):
        with self._lock:
            return self._force_tripped or self._tripped


class HealthMonitor(object):
    def report_success(self, response):
        self._failure_tracker.decrement()

    def report_failure(self, response):
        self._failure_tracker.increment()

    def report_exception(self, exc_type, exc_val, exc_tb):
        self._failure_tracker.increment()


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
    def __init__(
        self, circuit_breaker, health_monitor, fallback_func, failure_checker
    ):
        self._circuit_breaker = circuit_breaker
        self._fallback_func = fallback_func
        self._failure_checker = failure_checker
        self._health_monitor = health_monitor

    def before_request(self, request):
        if self._circuit_breaker.tripped:
            # Short-circuit.
            return transitions.finish(self._fallback_func(request))

    def after_response(self, request, response):
        if self._failure_checker.is_failure(response):
            self._health_monitor.report_failure(response)
            return transitions.finish(self._fallback_func(request))
        else:
            self._health_monitor.report_success(response)

    def after_exception(self, request, exc_type, exc_val, exc_tb):
        self._health_monitor.report_exception(exc_type, exc_val, exc_tb)
        if self._failure_checker.is_expected_exception(
            exc_type, exc_val, exc_tb
        ):
            return transitions.finish(self._fallback_func(request))
        return transitions.fail()
