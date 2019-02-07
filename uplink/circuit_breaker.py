# Standard library imports
import contextlib
import threading
import time

# Local imports
from uplink.clients.io import RequestTemplate, transitions


# Use monotonic time if available, otherwise fall back to the system clock.
now = time.monotonic if hasattr(time, "monotonic") else time.time


class CircuitBreakerOpenException(Exception):
    # TODO: Define body.
    pass


# Circuit breaker states from pg. 95 of Release It! (2nd Edition)
# by Michael T. Nygard


class CircuitBreakerState(object):
    def prepare(self, breaker):
        pass

    def is_closed(self):
        pass

    def on_success(self, breaker):
        pass

    def on_error(self, breaker, failure):
        pass


class Closed(CircuitBreakerState):
    def __init__(self, failure_counter):
        self._failure_counter = failure_counter

    def is_closed(self):
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

    def is_closed(self):
        # Fail fast.
        return False

    @property
    def period_remaining(self):
        return self._timeout - (self._clock() - self._start_time)


class HalfOpen(CircuitBreakerState):
    def __init__(self, failure_counter):
        self._failure_counter = failure_counter

    def is_closed(self):
        # TODO:
        #  Consider only letting the first call go through, and failing fast on
        #  all other calls.
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
    def is_closed(self):
        # Fail always.
        return False


class Disabled(CircuitBreakerState):
    def is_closed(self):
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
    def count_failure(self, failure):
        raise NotImplementedError

    def count_success(self):
        raise NotImplementedError

    def is_above_threshold(self):
        raise NotImplementedError

    def is_below_threshold(self):
        raise NotImplementedError


class BasicFailureCounter(FailureCounter):
    def __init__(self, decrement_every, buffer, failure_threshold, clock=now):
        self._window = decrement_every
        self._failure_threshold = failure_threshold
        self._failure_count = 0
        self._num_rounds = 0
        self._buffer = buffer
        self._diff = 0
        self._last_window = clock()
        self._clock = clock

    def decrement(self, n=1):
        assert n >= 0
        self._failure_count -= n
        self._num_rounds += 1

    def increment(self, n=1):
        self._failure_count += n
        self._num_rounds += 1

    def update(self):
        now_ = self._clock()
        windows_elapsed = int(max(now_ - self._last_window, 0) / self._window)
        self.decrement(windows_elapsed)
        self._last_window += self._window * windows_elapsed

    def count_success(self):
        self.update()
        self.decrement()

    def count_failure(self, failure):
        self.update()
        self.increment()

    def is_above_threshold(self):
        return (
            self._num_rounds >= self._buffer
            and self._failure_count > self._failure_threshold
        )

    def is_below_threshold(self):
        return (
            self._num_rounds >= self._buffer
            and self._failure_count < self._failure_threshold
        )


class CircuitBreaker(object):
    def reset(self):
        raise NotImplementedError

    def force_open(self):
        raise NotImplementedError

    def disable(self):
        raise NotImplementedError

    def attempt_reset(self):
        raise NotImplementedError

    def trip(self):
        raise NotImplementedError

    def on_success(self, request, response):
        raise NotImplementedError

    def on_error(self, request, failure):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    @property
    def closed(self):
        raise NotImplementedError

    @property
    def state(self):
        raise NotImplementedError


class BasicCircuitBreaker(CircuitBreaker):
    def __init__(self, failure_counter_factory, timeout_factory):
        # TODO: Find more appropriate names for these arguments
        self._failure_counter_factory = failure_counter_factory
        self._timeout_factory = timeout_factory
        self._timeout_generator = None
        self._state = None
        self.reset()

    def reset(self):
        self._state = Closed(self._failure_counter_factory.for_closed_state())

    def force_open(self):
        self._state = ForceOpened()

    def disable(self):
        self._state = Disabled()

    def attempt_reset(self):
        self._state = HalfOpen(
            self._failure_counter_factory.for_half_open_state()
        )

    def trip(self):
        # Don't reset timeout if the breaker is being opened from the half-open state.
        if self._timeout_generator is None or not isinstance(
            self._state, HalfOpen
        ):
            self._timeout_generator = self._timeout_factory()

        self._state = Open(next(self._timeout_generator), clock=now)

    def on_success(self, request, response):
        self._state.on_success(self)

    def on_error(self, request, failure):
        self._state.on_failure(self, failure)

    def update(self):
        self._state.prepare(self)

    @property
    def closed(self):
        return self._state.is_closed()

    @property
    def state(self):
        return self._state


class CircuitBreakerDecorator(CircuitBreaker):
    def __init__(self, breaker):
        self._breaker = breaker

    def reset(self):
        self._breaker.reset()

    def force_open(self):
        self._breaker.force_open()

    def disable(self):
        self._breaker.disble()

    def attempt_reset(self):
        self._breaker.attempt_reset()

    def trip(self):
        self._breaker.trip()

    def on_success(self, request, response):
        self._breaker.on_success(request, response)

    def on_error(self, request, failure):
        self._breaker.on_error(request, failure)

    def update(self):
        self._breaker.update()

    @property
    def state(self):
        return self._breaker.state

    @property
    def closed(self):
        return self._breaker.closed


@contextlib.contextmanager
def _monitor_state_transition(breaker, monitor):
    from_state = type(breaker.state)
    yield
    monitor.on_state_transistion(from_state, type(breaker.state))


class MonitoringCircuitBreaker(CircuitBreakerDecorator):
    def __init__(self, breaker, monitor):
        super(MonitoringCircuitBreaker, self).__init__(breaker)
        self._monitor = monitor

    def _monitor_state_transition(self):
        return _monitor_state_transition(self._breaker, self._monitor)

    def reset(self):
        with self._monitor_state_transition():
            super(MonitoringCircuitBreaker, self).reset()

    def force_open(self):
        with self._monitor_state_transition():
            super(MonitoringCircuitBreaker, self).force_open()

    def disable(self):
        with self._monitor_state_transition():
            super(MonitoringCircuitBreaker, self).disable()

    def attempt_reset(self):
        with self._monitor_state_transition():
            super(MonitoringCircuitBreaker, self).attempt_reset()

    def trip(self):
        with self._monitor_state_transition():
            super(MonitoringCircuitBreaker, self).reset()

    def on_success(self, request, response):
        self._monitor.on_success(request, response)
        super(MonitoringCircuitBreaker, self).on_success(request, response)

    def on_error(self, request, failure):
        self._monitor.on_error(request, failure)
        super(MonitoringCircuitBreaker, self).on_error(request, failure)


class AtomicCircuitBreaker(CircuitBreakerDecorator):
    def __init__(self, breaker):
        super(AtomicCircuitBreaker, self).__init__(breaker)
        self._lock = threading.RLock()

    def reset(self):
        with self._lock:
            super(AtomicCircuitBreaker, self).reset()

    def force_open(self):
        with self._lock:
            super(AtomicCircuitBreaker, self).force_open()

    def disable(self):
        with self._lock:
            super(AtomicCircuitBreaker, self).disable()

    def on_success(self, request, response):
        with self._lock:
            super(AtomicCircuitBreaker, self).on_success(request, response)

    def on_error(self, request, failure):
        with self._lock:
            super(AtomicCircuitBreaker, self).on_error(request, failure)

    def update(self):
        with self._lock:
            super(AtomicCircuitBreaker, self).update()


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
    def __init__(self, breaker, fallback, monitor, failure_factory):
        self._breaker = breaker
        self._fallback = fallback
        self._monitor = monitor
        self._failure_factory = failure_factory

    def before_request(self, request):
        self._breaker.update()

        if not self._breaker.closed:
            self._monitor.on_request_not_permitted(request)

            if not callable(self._fallback):
                raise CircuitBreakerOpenException()

            # Short-circuit.
            return transitions.finish(self._fallback(request))

    def _handle_failure(self, request, failure):
        self._breaker.on_failure(request, failure)

        if callable(self._fallback):
            return transitions.finish(self._fallback(request))

    def after_response(self, request, response):
        failure = self._failure_factory.from_response(response)
        if failure is None:
            self._breaker.on_success(request, response)
        else:
            return self._handle_failure(request, failure)

    def after_exception(self, request, exc_type, exc_val, exc_tb):
        failure = self._failure_factory.from_exception(exc_val)
        if failure is not None:
            return self._handle_failure(request, failure)
        else:
            self._monitor.on_ignored_error(request, exc_val)
