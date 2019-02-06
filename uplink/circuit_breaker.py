# Standard library imports
import contextlib
import threading
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
        self._failure_counter.count_success()

    def on_error(self, breaker, failure):
        self._failure_counter.count_failure(failure)

        # Trip breaker if threshold reached
        if self._failure_counter.is_above_threshold():
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
    def __init__(self, failure_counter):
        self._failure_counter = failure_counter

    def is_closed(self, breaker):
        # Pass through.
        return True

    def on_success(self, breaker):
        self._failure_counter.count_success()

        # Reset circuit.
        if self._failure_counter.is_below_threshold():
            breaker.reset()

    def on_error(self, breaker, failure):
        self._failure_counter.count_failure(failure)

        # Trip breaker.
        if self._failure_counter.is_above_threshold():
            breaker.trip()


class ForceOpened(CircuitBreakerState):
    def is_closed(self, breaker):
        # Fail always.
        return False


class Disabled(CircuitBreakerState):
    def is_closed(self, breaker):
        # Pass through always.
        return True


class Failure(object):
    def __init__(self, exception=None, status_code=None):
        self._exception = exception
        self._status_code = status_code

    @staticmethod
    def of_response(response):
        return Failure(status_code=response.status_code)

    @staticmethod
    def of_exception(exception):
        return Failure(exception=exception)

    def is_exception(self):
        return self._exception is not None

    @property
    def exception(self):
        return self._exception

    @property
    def status_code(self):
        return self._status_code


class FailureCounter(object):
    def count(self, failure):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError


class BreakerContext(object):
    def __init__(self, failure_counter_factory, timeout):
        self._failure_counter_factory = failure_counter_factory
        self._timeout = timeout
        self._state = None

    def reset(self):
        self._state = Closed(self._failure_counter_factory())

    def force_open(self):
        self._state = ForceOpened()

    def disable(self):
        self._state = Disabled()

    def attempt_reset(self):
        self._state = HalfOpen(self._failure_counter_factory())

    def trip(self):
        self._state = Open(self._timeout, clock=now)

    @property
    def state(self):
        return self._state


@contextlib.contextmanager
def _monitor_state_transition(context, monitor):
    from_state = type(context.state)
    yield
    monitor.on_state_transistion(from_state, type(context.state))


class MonitoringContextWrapper(object):
    def __init__(self, context, monitor):
        self._context = context
        self._monitor = monitor

    def _monitor(self):
        return _monitor_state_transition(self._context, self._monitor)

    def reset(self):
        with self._monitor():
            self._context.reset()

    def force_open(self):
        with self._monitor():
            self._context.force_open()

    def disable(self):
        with self._monitor():
            self._context.disable()

    def attempt_reset(self):
        with self._monitor():
            self._context.attempt_reset()

    def trip(self):
        with self._monitor():
            self._context.trip()

    @property
    def state(self):
        return self._state


class CircuitBreaker(object):
    def __init__(self, context, monitor):
        self._context = context
        self._monitor = monitor
        self._context.reset()
        self._lock = threading.RLock()

    @property
    def _monitored_context(self):
        return MonitoringContextWrapper(self._context, self._monitor)

    def reset(self):
        with self._lock:
            self._monitored_context.reset()

    def force_open(self):
        with self._lock:
            self._monitored_context.force_open()

    def disable(self):
        with self._lock:
            self._monitored_context.disable()

    def on_success(self, request, response):
        with self._lock:
            self._monitor.on_success(request, response)
            self._context.state.on_success(self._monitored_context)

    def on_error(self, request, failure):
        with self._lock:
            self._monitor.on_error(request, failure)
            self._context.state.on_error(self._monitored_context, failure)

    def update(self):
        with self._lock:
            self._context.state.prepare(self._monitored_context)

    @property
    def closed(self):
        return self._context.state.is_closed()


class HealthMonitor(object):
    def on_state_transition(self, from_state, to_state):
        pass

    def on_success(self, request, response):
        pass

    def on_error(self, request, failure):
        pass

    def on_ignored_error(self, request, failure):
        pass

    def on_request_not_permitted(self, request):
        pass


class FailureFactory(object):
    def from_response(self, response):
        raise NotImplementedError

    def from_exception(self, exception):
        raise NotImplementedError


class BasicFailureFactory(FailureFactory):
    def from_response(self, response):
        return None

    def from_exception(self, exception):
        return Failure.of_exception(exception=exception)


class CircuitRequestTemplate(RequestTemplate):
    def __init__(self, circuit_breaker, fallback, monitor, failure_factory):
        self._circuit_breaker = circuit_breaker
        self._fallback = fallback
        self._monitor = monitor
        self._failure_factory = failure_factory

    def before_request(self, request):
        self._circuit_breaker.update()

        if not self._circuit_breaker.closed:
            self._monitor.on_request_not_permitted(request)

            if not callable(self._fallback):
                raise CircuitBreakerOpen()

            # Short-circuit.
            return transitions.finish(self._fallback(request))

    def _handle_failure(self, request, failure):
        self._circuit_breaker.on_failure(request, failure)

        if callable(self._fallback):
            return transitions.finish(self._fallback(request))

    def after_response(self, request, response):
        failure = self._failure_factory.from_response(response)
        if failure is None:
            self._circuit_breaker.on_success(request, response)
        else:
            return self._handle_failure(request, failure)

    def after_exception(self, request, exc_type, exc_val, exc_tb):
        failure = self._failure_factory.from_exception(exc_val)
        if failure is not None:
            return self._handle_failure(request, failure)
        else:
            self._monitor.on_ignored_error(request, exc_val)
