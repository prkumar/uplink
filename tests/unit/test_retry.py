# Local imports
from uplink import retry
from uplink.retry import backoff, stop


def test_jittered_backoff():
    iterator = backoff.jittered()()

    first = next(iterator)
    assert 0 <= first <= 1

    second = next(iterator)
    assert 0 <= second <= 2

    third = next(iterator)
    assert 0 <= third <= 4

    fourth = next(iterator)
    assert 0 <= fourth <= 8

    fifth = next(iterator)
    assert 0 <= fifth <= 16


def test_exponential_backoff_minimum():
    iterator = backoff.exponential(base=2, minimum=8)()
    assert next(iterator) == 8
    assert next(iterator) == 16


def test_fixed_backoff():
    iterator = backoff.fixed(10)()
    assert next(iterator) == 10
    assert next(iterator) == 10
    assert next(iterator) == 10


def test_retry_stop_default():
    decorator = retry()
    assert stop.DISABLE == decorator._stop
    assert not decorator._stop()


def test_retry_custom_stop():
    def custom_stop(*_):
        return True

    decorator = retry(stop=custom_stop)
    assert decorator._stop == custom_stop


def test_retry_backoff():
    def custom_backoff(*_):
        return True

    decorator = retry(backoff=custom_backoff)
    assert decorator._backoff == custom_backoff


def test_retry_decorator_exposes_submodules_as_properties():
    assert retry.backoff is backoff
    assert retry.stop is stop


class TestClientExceptionProxies(object):
    @staticmethod
    def _get_exception(proxy, request_builder):
        return proxy(request_builder.client.exceptions)

    def test_basic_client_exception(self, request_builder):
        exc = self._get_exception(retry.BASE_CLIENT_EXCEPTION, request_builder)
        assert request_builder.client.exceptions.BaseClientException == exc

    def test_connection_error(self, request_builder):
        exc = self._get_exception(retry.CONNECTION_ERROR, request_builder)
        assert request_builder.client.exceptions.BaseClientException == exc

    def test_connection_timeout(self, request_builder):
        exc = self._get_exception(retry.CONNECTION_TIMEOUT, request_builder)
        assert request_builder.client.exceptions.BaseClientException == exc

    def test_server_timeout(self, request_builder):
        exc = self._get_exception(retry.SERVER_TIMEOUT, request_builder)
        assert request_builder.client.exceptions.BaseClientException == exc

    def test_ssl_error(self, request_builder):
        exc = self._get_exception(retry.SSL_ERROR, request_builder)
        assert request_builder.client.exceptions.BaseClientException == exc
