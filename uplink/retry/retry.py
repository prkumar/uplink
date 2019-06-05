# Local imports
from uplink import decorators
from uplink.clients.io import RequestTemplate, transitions
from uplink.retry import (
    when as when_mod,
    stop as stop_mod,
    backoff as backoff_mod,
)
from uplink.retry._helpers import ClientExceptionProxy

__all__ = ["retry"]


class RetryTemplate(RequestTemplate):
    def __init__(self, backoff, retry_condition):
        self._backoff = backoff
        self._backoff_iterator = None
        self._condition = retry_condition
        self._reset()

    def _next_delay(self):
        try:
            delay = next(self._backoff_iterator)
        except StopIteration:
            # Fallback to the default behavior
            pass
        else:
            return transitions.sleep(delay)

    def _reset(self):
        self._backoff_iterator = self._backoff()

    def after_response(self, request, response):
        if self._condition.should_retry_after_response(response):
            return self._next_delay()
        else:
            self._reset()

    def after_exception(self, request, exc_type, exc_val, exc_tb):
        if self._condition.should_retry_after_exception(
            exc_type, exc_val, exc_tb
        ):
            return self._next_delay()
        else:
            self._reset()


# noinspection PyPep8Naming
class retry(decorators.MethodAnnotation):
    """
    A decorator that adds retry support to a consumer method or to an
    entire consumer.

    Unless you specify the ``when`` or ``on_exception`` argument, all
    failed requests that raise an exception are retried.

    Unless you specify the ``max_attempts`` or ``stop`` argument, this
    decorator continues retrying until the server returns a response.

    Unless you specify the ``backoff`` argument, this decorator uses
    `capped exponential backoff and jitter <https://amzn.to/2xc2nK2>`_,
    which should benefit performance with remote services under high
    contention.

    .. note::

        Response and error handlers (see :ref:`here <custom response
        handler>`) are invoked after the retry condition breaks or all
        retry attempts are exhausted, whatever comes first. These
        handlers will receive the first response/exception that triggers
        the retry's ``stop`` condition or doesn't match its ``when``
        filter.

        In other words, responses or exceptions that match
        the retry condition (e.g., retry when status code is 5xx) are
        not subject to response or error handlers as long as the request
        doesn't break the retry's stop condition (e.g., stop retrying
        after 5 attempts).

    Args:
        when (optional): A predicate that determines when a retry
            should be attempted.
        max_attempts (int, optional): The number of retries to attempt.
            If not specified, requests are retried continuously until
            a response is rendered.
        on_exception (:class:`Exception`, optional): The exception type
            that should prompt a retry attempt.
        stop (:obj:`callable`, optional): A function that creates
            predicates that decide when to stop retrying a request.
        backoff (:obj:`callable`, optional): A function that creates
            an iterator over the ordered sequence of timeouts between
            retries. If not specified, exponential backoff is used.
    """

    _DEFAULT_PREDICATE = when_mod.raises(Exception)

    def __init__(
        self,
        when=None,
        max_attempts=None,
        on_exception=None,
        stop=None,
        backoff=None,
    ):
        if stop is not None:
            self._stop = stop
        elif max_attempts is not None:
            self._stop = stop_mod.after_attempt(max_attempts)
        else:
            self._stop = stop_mod.NEVER

        self._predicate = when

        if on_exception is not None:
            self._predicate = when_mod.raises(on_exception) | self._predicate

        if self._predicate is None:
            self._predicate = self._DEFAULT_PREDICATE

        self._backoff = backoff_mod.jittered() if backoff is None else backoff

    BASE_CLIENT_EXCEPTION = ClientExceptionProxy(
        lambda ex: ex.BaseClientException
    )
    CONNECTION_ERROR = ClientExceptionProxy(lambda ex: ex.ConnectionError)
    CONNECTION_TIMEOUT = ClientExceptionProxy(lambda ex: ex.ConnectionTimeout)
    SERVER_TIMEOUT = ClientExceptionProxy(lambda ex: ex.ServerTimeout)
    SSL_ERROR = ClientExceptionProxy(lambda ex: ex.SSLError)

    def modify_request(self, request_builder):
        request_builder.add_request_template(
            self._create_template(request_builder)
        )

    def _create_template(self, request_builder):
        return RetryTemplate(
            self._backoff_iterator, self._predicate(request_builder)
        )

    def _backoff_iterator(self):
        stop_gen = self._stop()
        for delay in self._backoff():
            next(stop_gen)
            if stop_gen.send(delay):
                break
            yield delay

    stop = stop_mod
    backoff = backoff_mod
    when = when_mod
