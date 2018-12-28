# Local imports
from uplink import retry


def test_jittered_backoff():
    backoff = retry.jittered_backoff()()

    first = next(backoff)
    assert 0 <= first <= 1

    second = next(backoff)
    assert 0 <= second <= 2

    third = next(backoff)
    assert 0 <= third <= 4

    fourth = next(backoff)
    assert 0 <= fourth <= 8

    fifth = next(backoff)
    assert 0 <= fifth <= 16


def test_exponential_backoff_minimum():
    backoff = retry.exponential_backoff(base=2, minimum=8)()
    assert next(backoff) == 8
    assert next(backoff) == 16


def test_fixed_backoff():
    backoff = retry.fixed_backoff(10)()
    assert next(backoff) == 10
    assert next(backoff) == 10
    assert next(backoff) == 10


def test_retry_stop_default():
    decorator = retry()
    assert retry.STOP_NEVER == decorator.stop
    assert not decorator.stop()()


def test_retry_custom_stop():
    def custom_stop(*_):
        return True

    decorator = retry(stop=custom_stop)
    assert decorator.stop == custom_stop


def test_retry_wait():
    def custom_wait(*_):
        return True

    decorator = retry(wait=custom_wait)
    assert decorator.wait == custom_wait


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
