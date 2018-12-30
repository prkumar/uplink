# Local imports
from uplink import decorators
from uplink.clients.io import RequestTemplate, transitions
from uplink.retry import stop as stop_mod, backoff as backoff_mod

__all__ = ["retry"]


class _ClientExceptionProxy(object):
    def __init__(self, getter):
        self._getter = getter

    @classmethod
    def wrap_proxy_if_necessary(cls, exc):
        return exc if isinstance(exc, cls) else (lambda exceptions: exc)

    def __call__(self, exceptions):
        return self._getter(exceptions)


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


# noinspection PyPep8Naming
class retry(decorators.MethodAnnotation):
    """
    A decorator that adds retry support to a consumer method or to an
    entire consumer.

    Unless you specify the ``on_exception`` argument, all failed
    requests are retried.

    Unless you specify the ``max_attempts`` or ``stop`` argument, this
    decorator continues retrying until the server returns a response.

    Unless you specify the ``wait`` argument, this decorator uses
    `capped exponential backoff and jitter <https://amzn.to/2xc2nK2>`_,
    which should benefit performance with remote services under high
    contention.

    Args:
        max_attempts (int, optional): The number of retries to attempt.
            If not specified, requests are retried continuously until
            a response is rendered.
        on_exception (:class:`Exception`, optional): The exception type
            that should prompt a retry attempt. The default value is
            :class:`Exception`, meaning all failed requests are
            retried.
        stop (:obj:`callable`, optional): A function that creates
            predicates that decide when to stop retrying a request.
        backoff (:obj:`callable`, optional): A function that creates
            an iterator over the ordered sequence of timeouts between
            retries. If not specified, exponential backoff is used.
    """

    def __init__(
        self, max_attempts=None, on_exception=Exception, stop=None, backoff=None
    ):
        if stop is not None:
            self._stop = stop
        elif max_attempts is not None:
            self._stop = stop_mod.after_attempts(max_attempts)
        else:
            self._stop = stop_mod.DISABLE

        self._backoff = backoff_mod.jittered() if backoff is None else backoff
        self._when = self._when_exception_type_is(on_exception)

    BASE_CLIENT_EXCEPTION = _ClientExceptionProxy(
        lambda ex: ex.BaseClientException
    )
    CONNECTION_ERROR = _ClientExceptionProxy(lambda ex: ex.ConnectionError)
    CONNECTION_TIMEOUT = _ClientExceptionProxy(lambda ex: ex.ConnectionTimeout)
    SERVER_TIMEOUT = _ClientExceptionProxy(lambda ex: ex.ServerTimeout)
    SSL_ERROR = _ClientExceptionProxy(lambda ex: ex.SSLError)

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
        should_stop = self._stop()
        for delay in self._backoff():
            if should_stop():
                break
            yield delay

    stop = stop_mod
    backoff = backoff_mod
