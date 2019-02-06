# Standard library imports
import time

# Local imports
from uplink.clients.io import RequestTemplate, transitions


# Use monotonic time if available, otherwise fall back to the system clock.
now = time.monotonic if hasattr(time, "monotonic") else time.time


class CircuitBreakerOpen(Exception):
    # TODO: Define body.
    pass


# Circuit breaker states from pg. 95 of Release It! (2nd Edition)
# by Michael T. Nygard


class CircuitBreakerState(object):
    def prepare(self, breaker):
        pass

    def is_closed(self, breaker):
        pass

    def on_success(self, breaker):
        pass

    def on_error(self, breaker, failure):
        pass


class Closed(CircuitBreakerState):
    def __init__(self, failure_counter):
        self._failure_counter = failure_counter

    def is_closed(self, breaker):
        # Pass through.
        return True

    def on_success(self, breaker):
        # Reset count.
        self._failure_counter.reset()

    def on_error(self, breaker, failure):
        # Count failure.
        self._failure_counter.count(failure)

        # Trip breaker if threshold reached
        if self._failure_counter.has_exceeded_treshold():
            breaker.trip()


class Open(CircuitBreakerState):
    def __init__(self, timeout, clock):
        self._timeout = timeout
        self._clock = clock
        self._start_time = clock()

    def prepare(self, breaker):
        # On timeout, attempt reset.
        if self.period_remaining <= 0:
            breaker.attempt_reset()

    def is_closed(self, breaker):
        # Fail fast.
        return False

    @property
    def period_remaining(self):
        return self._timeout - (self._clock() - self._start_time)


class HalfOpen(CircuitBreakerState):
    def is_closed(self, breaker):
        # Pass through.
        return True

    def on_success(self, breaker):
        # Reset circuit.
        breaker.reset()

    def on_error(self, breaker):
        # Trip breaker.
        breaker.trip()


class ForceOpened(CircuitBreakerState):
    def is_closed(self, breaker):
        # Fail always.
        return False


class Disabled(CircuitBreakerState):
    def is_closed(self, breaker):
        # Pass through always.
        return True


class FailureCounter(object):
    def count(self, failure):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError


class BaseCircuitBreaker(object):
    def __init__(self, timeout, failure_counter, health_monitor):
        self._timeout = timeout
        self._health_monitor = health_monitor
        self._failure_counter = failure_counter
        self._state = None
        self.reset()

    def reset(self):
        self._state = Closed(self._failure_counter)

    def force_open(self):
        self._state = ForceOpened()

    def disable(self):
        self._state = Disabled()

    def attempt_reset(self):
        self._state = HalfOpen()

    def trip(self):
        self._state = Open(self._timeout, clock=now)

    def on_success(self, request, response):
        self._health_monitor.report_success(request, response)
        self._state.on_success(self)

    def on_failure(self, request, failure):
        self._health_monitor.report_failure(request, failure)
        self._state.on_failure(self, failure)

    @property
    def closed(self):
        self._state.prepare(self)
        return self._state.is_closed()


class HealthMonitor(object):
    def report_success(self, response):
        pass

    def report_failure(self, failure):
        pass


class FailureFactory(object):
    def from_response(self, response):
        raise NotImplementedError

    def from_exception(self, exc_val):
        raise NotImplementedError


class CircuitRequestTemplate(RequestTemplate):
    def __init__(self, circuit_breaker, fallback, failure_factory):
        self._circuit_breaker = circuit_breaker
        self._fallback = fallback
        self._failure_factory = failure_factory

    def before_request(self, request):
        if not self._circuit_breaker.closed:
            if not callable(self._fallback):
                raise CircuitBreakerOpen()

            # Short-circuit.
            return transitions.finish(self._fallback(request))

    def after_response(self, request, response):
        failure = self._failure_factory.from_response(response)
        if failure is None:
            self._circuit_breaker.on_success(request, response)
        else:
            self._circuit_breaker.on_failure(request, failure)

    def after_exception(self, request, exc_type, exc_val, exc_tb):
        failure = self._failure_factory.from_exception(exc_val)
        self._circuit_breaker.on_failure(request, failure)
        if callable(self._fallback):
            return transitions.finish(self._fallback(request))
