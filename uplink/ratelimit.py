# Standard library imports
import contextlib
import math
import threading
import time
import sys

# Local imports
from uplink import decorators
from uplink.clients.io import RequestTemplate, transitions

__all__ = ["ratelimit"]

# Use monotonic time if available, otherwise fall back to the system clock.
now = time.monotonic if hasattr(time, "monotonic") else time.time


class Limiter(object):
    _last_reset = _num_calls = None

    def __init__(self, max_calls, period, clock):
        self._max_calls = max_calls
        self._period = period
        self._clock = clock
        self._lock = threading.RLock()
        self._reset()

    @property
    def period_remaining(self):
        return self._period - (self._clock() - self._last_reset)

    @contextlib.contextmanager
    def check(self):
        with self._lock:
            if self.period_remaining <= 0:
                self._reset()
            yield self._max_calls > self._num_calls
            self._num_calls += 1

    def _reset(self):
        self._num_calls = 0
        self._last_reset = self._clock()


class RateLimiterTemplate(RequestTemplate):
    def __init__(self, limiter):
        self._limiter = limiter

    def before_request(self, request):
        with self._limiter.check() as ok:
            if ok:
                return transitions.send(request)
            else:
                return transitions.sleep(self._limiter.period_remaining)


# noinspection PyPep8Naming
class ratelimit(decorators.MethodAnnotation):
    """
    A decorator that constrains the decorated consumer method or
    consumer to making a specified maximum number of requests within a
    defined time period (e.g., 15 calls every 15 minutes).

    Args:
        calls (int): The maximum number of allowed calls that the
            consumer can make within the time period.
        period (float): The duration of each time period in seconds.
    """

    def __init__(self, calls=15, period=900, clock=now):
        self._max_calls = max(1, min(sys.maxsize, math.floor(calls)))
        self._period = period
        self._clock = clock
        self._limiter = None

    def _get_limiter_for_request(self, _):
        if self._limiter is None:
            self._limiter = Limiter(self._max_calls, self._period, self._clock)
        return self._limiter

    def modify_request(self, request_builder):
        limiter = self._get_limiter_for_request(request_builder)
        request_builder.add_request_template(RateLimiterTemplate(limiter))
