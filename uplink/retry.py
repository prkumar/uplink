# Standard library imports
import random
import sys

# Local imports
from uplink import decorators
from uplink.clients.io import RequestTemplate, transitions

__all__ = ["retry"]

# Constants
MAX_VALUE = sys.maxsize


class RetryTemplate(RequestTemplate):
    def __init__(self, back_off_iterator, failure_tester):
        self._back_off_iterator = back_off_iterator
        self._should_retry = failure_tester

    def after_exception(self, request, exc_type, exc_val, exc_tb):
        if self._should_retry(exc_type, exc_val, exc_tb):
            try:
                delay = next(self._back_off_iterator)
            except StopIteration:
                # Fallback to the default behavior
                pass
            else:
                return transitions.sleep(delay)


class _AfterAttemptStopper(object):
    def __init__(self, num):
        self._num = num
        self._attempt = 0

    def __call__(self, *_):
        self._attempt += 1
        return self._num > self._attempt

    @property
    def num(self):
        return self._num

    @property
    def attempt(self):
        return self._attempt

    def __eq__(self, other):
        return (
            isinstance(other, _AfterAttemptStopper)
            and other.num == self.num
            and other.attempt == self.attempt
        )


# noinspection PyPep8Naming
class retry(decorators.MethodAnnotation):
    """
    A decorator that adds retry support to a consumer method or to an
    entire consumer.

    Unless you override the ``wait`` argument, this decorator uses
    `capped exponential backoff and jitter <https://amzn.to/2xc2nK2>`_,
    which should benefit performance with remote services under high
    contention.

    Args:
        max_attempts (int, optional): The number of retries to attempt.
            If specified, retries are capped at this limit.
        stop (:obj:`callable`, optional): A function that creates
            predicates that decide when to stop retrying a request.
        wait (:obj:`callable`, optional): A function that creates
            an iterator over the ordered sequence of timeouts between
            retries. If not specified, exponential backoff is used.
    """

    @staticmethod
    def _stop_never():
        return lambda *_: True

    STOP_NEVER = _stop_never

    @staticmethod
    def jittered_backoff(base=2, multiplier=1, minimum=0, maximum=MAX_VALUE):
        """
        Waits using capped exponential backoff and full jitter.

        The implementation is discussed in `this AWS Architecture Blog
        post <https://amzn.to/2xc2nK2>`_, which recommends this approach
        for any remote clients, as it minimizes the total completion
        time of competing clients in a distributed system experiencing
        high contention.
        """

        def wait_iterator():
            backoff = retry.exponential_backoff(
                base, multiplier, minimum, maximum
            )
            for delay in backoff:
                yield random.uniform(0, 1) * delay

        return wait_iterator

    @staticmethod
    def exponential_backoff(base=2, multiplier=1, minimum=0, maximum=MAX_VALUE):
        """
        Waits using capped exponential backoff, meaning that the delay
        is multiplied by a constant ``base`` after each attempt, up to
        an optional ``maximum`` value.
        """

        def wait_iterator():
            delay = base * multiplier
            while minimum > delay:
                delay *= base
            while maximum >= delay:
                yield delay
                delay *= base
            while True:
                yield maximum

        return wait_iterator

    @staticmethod
    def fixed_backoff(seconds):
        """Waits for a fixed number of ``seconds`` before each retry."""

        def wait_iterator():
            while True:
                yield seconds

        return wait_iterator

    @staticmethod
    def stop_after_attempt(attempts):
        """Stops retrying after the specified number of ``attempts``."""

        def stop():
            return _AfterAttemptStopper(attempts)

        return stop

    def __init__(self, max_attempts=None, stop=None, wait=None):
        if stop is not None:
            self._stop = stop
        elif max_attempts is not None:
            self._stop = self.stop_after_attempt(max_attempts)
        else:
            self._stop = self.STOP_NEVER

        self._wait = self.jittered_backoff() if wait is None else wait

    def modify_request(self, request_builder):
        request_builder.add_request_template(self._create_template())

    def _create_template(self):
        return RetryTemplate(self._wait(), self._stop())

    @property
    def stop(self):
        return self._stop

    @property
    def wait(self):
        return self._wait
