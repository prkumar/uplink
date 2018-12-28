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
        return self._num <= self._attempt


class _ClientExceptionProxy(object):
    def __init__(self, getter):
        self._getter = getter

    @classmethod
    def wrap_proxy_if_necessary(cls, exc):
        return exc if isinstance(exc, cls) else (lambda exceptions: exc)

    def __call__(self, exceptions):
        return self._getter(exceptions)


# noinspection PyPep8Naming
class retry(decorators.MethodAnnotation):
    """
    A decorator that adds retry support to a consumer method or to an
    entire consumer.

    Unless you specify the ``max_attempts`` or ``stop`` argument, this
    decorator continues retrying until the server returns a response.

    Unless you specify the ``wait`` argument, this decorator uses
    `capped exponential backoff and jitter <https://amzn.to/2xc2nK2>`_,
    which should benefit performance with remote services under high
    contention.

    Args:
        max_attempts (int, optional): The number of retries to attempt.
            If specified, retries are capped at this limit.
        when_raises (:class:`Exception`, optional): The base exception
            type that should prompt a retry attempt. The default value
            is :class:`Exception`, meaning all failed requests are
            retried.
        stop (:obj:`callable`, optional): A function that creates
            predicates that decide when to stop retrying a request.
        wait (:obj:`callable`, optional): A function that creates
            an iterator over the ordered sequence of timeouts between
            retries. If not specified, exponential backoff is used.
    """

    def __init__(
        self, max_attempts=None, when_raises=Exception, stop=None, wait=None
    ):
        if stop is not None:
            self._stop = stop
        elif max_attempts is not None:
            self._stop = self.stop_after_attempts(max_attempts)
        else:
            self._stop = self.STOP_NEVER

        self._wait = self.jittered_backoff() if wait is None else wait
        self._when = self._when_exception_type_is(when_raises)

    BASE_CLIENT_EXCEPTION = _ClientExceptionProxy(
        lambda ex: ex.BaseClientException
    )
    CONNECTION_ERROR = _ClientExceptionProxy(lambda ex: ex.ConnectionError)
    CONNECTION_TIMEOUT = _ClientExceptionProxy(lambda ex: ex.ConnectionTimeout)
    SERVER_TIMEOUT = _ClientExceptionProxy(lambda ex: ex.ServerTimeout)
    SSL_ERROR = _ClientExceptionProxy(lambda ex: ex.SSLError)

    @staticmethod
    def _stop_never():
        return lambda *_: False

    STOP_NEVER = _stop_never
    """Continues retrying until the request is successful"""

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
        backoff = retry.exponential_backoff(base, multiplier, minimum, maximum)
        return lambda *_: iter(
            random.uniform(0, 1) * delay for delay in backoff()
        )  # pragma: no cover

    @staticmethod
    def exponential_backoff(base=2, multiplier=1, minimum=0, maximum=MAX_VALUE):
        """
        Waits using capped exponential backoff, meaning that the delay
        is multiplied by a constant ``base`` after each attempt, up to
        an optional ``maximum`` value.
        """

        def wait_iterator():
            delay = multiplier
            while minimum > delay:
                delay *= base
            while True:
                yield min(delay, maximum)
                delay *= base

        return wait_iterator

    @staticmethod
    def fixed_backoff(seconds):
        """Waits for a fixed number of ``seconds`` before each retry."""

        def wait_iterator():
            while True:
                yield seconds

        return wait_iterator

    @staticmethod
    def stop_after_attempts(attempts):
        """Stops retrying after the specified number of ``attempts``."""

        def stop():
            return _AfterAttemptStopper(attempts)

        return stop

    @staticmethod
    def _when_exception_type_is(exc_type):
        """
        Attempts retry when the raised exception type is ``exc_type``.
        """
        proxy = _ClientExceptionProxy.wrap_proxy_if_necessary(exc_type)

        def when_func(rb):
            type_ = proxy(rb.client.exceptions)

            def should_retry(et, ev, tb):
                return isinstance(ev, type_)

            return should_retry

        return when_func

    def modify_request(self, request_builder):
        request_builder.add_request_template(
            self._create_template(request_builder)
        )

    def _create_template(self, request_builder):
        return RetryTemplate(
            self._backoff_iterator(), self._when(request_builder)
        )

    def _backoff_iterator(self):
        stop = self._stop()
        for delay in self._wait():
            if stop():
                break
            yield delay

    @property
    def stop(self):
        return self._stop

    @property
    def wait(self):
        return self._wait
