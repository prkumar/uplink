# Local imports
from uplink import retry
from uplink.retry import backoff, stop, when


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


def test_compose_backoff(mocker):
    left = backoff.from_iterable([0, 1])
    right = backoff.from_iterable([2])
    mocker.spy(left, "handle_after_final_retry")
    mocker.spy(right, "handle_after_final_retry")
    strategy = left | right

    # Should return None after both strategies are exhausted
    assert strategy.get_timeout_after_response(None, None) == 0
    assert strategy.get_timeout_after_exception(None, None, None, None) == 1
    assert strategy.get_timeout_after_response(None, None) == 2
    assert strategy.get_timeout_after_exception(None, None, None, None) is None

    # Should invoke both strategies after_stop method
    strategy.handle_after_final_retry()

    left.handle_after_final_retry.assert_called_once_with()
    right.handle_after_final_retry.assert_called_once_with()


def test_retry_stop_default():
    decorator = retry()
    assert stop.NEVER == decorator._stop

    stop_gen = decorator._stop()

    next(stop_gen)
    assert stop_gen.send(1) is False

    next(stop_gen)
    assert stop_gen.send(5) is False

    next(stop_gen)
    assert stop_gen.send(10) is False

    next(stop_gen)
    assert stop_gen.send(10.1) is False


def test_stop_or():
    stop_gen = (stop.after_delay(2) | stop.after_attempt(3))()

    next(stop_gen)
    assert stop_gen.send(3) is True

    next(stop_gen)
    assert stop_gen.send(1) is False

    next(stop_gen)
    assert stop_gen.send(5) is True

    next(stop_gen)
    assert stop_gen.send(1) is True


def test_stop_or_with_none():
    stop1 = stop.after_delay(2)
    assert stop1 is (stop1 | None)


def test_retry_decorator_exposes_submodules_as_properties():
    assert retry.backoff is backoff
    assert retry.stop is stop
    assert retry.when is when


def test_stop_after_delay():
    stop_gen = stop.after_delay(10)()

    # Start generator
    next(stop_gen)
    assert stop_gen.send(1) is False

    next(stop_gen)
    assert stop_gen.send(5) is False

    next(stop_gen)
    assert stop_gen.send(10) is False

    next(stop_gen)
    assert stop_gen.send(10.1) is True


def test_when_status(mocker, request_builder):
    # Setup
    response = mocker.Mock()
    response.status_code = 401

    # Verify: Returns self on call
    predicate = when.status(401)
    assert predicate(request_builder) is predicate

    # Verify: Encountered expected status
    assert when.status(401).should_retry_after_response(response) is True

    # Verify: Encountered unexpected status
    assert when.status(200).should_retry_after_response(response) is False

    # Verify: Should return false for exceptions
    assert (
        when.status(401).should_retry_after_exception(
            Exception, Exception(), None
        )
        is False
    )


def test_when_status_5xx(mocker, request_builder):
    # Setup
    response = mocker.Mock()
    response.status_code = 501

    # Verify: Returns self on call
    predicate = when.status_5xx()
    assert predicate(request_builder) is predicate

    # Verify: Encountered bad request status
    assert when.status_5xx().should_retry_after_response(response) is True

    # Verify: Encountered successful request status
    response.status_code = 200
    assert when.status_5xx().should_retry_after_response(response) is False

    # Verify: Should return false for exceptions
    assert (
        when.status_5xx().should_retry_after_exception(
            Exception, Exception(), None
        )
        is False
    )


def test_when_or_operator_with_response(mocker):
    # Setup
    response = mocker.Mock()
    response.status_code = 401
    predicate = when.status(401) | when.status(405)

    # Verify: when left predicate matches
    assert predicate.should_retry_after_response(response) is True

    # Verify: when right predicate matches
    response.status_code = 405
    assert predicate.should_retry_after_response(response) is True

    # Verify: when neither matches
    response.status_code = 200
    assert predicate.should_retry_after_response(response) is False


def test_when_or_operator_with_exception(mocker, request_builder):
    # Setup
    response = mocker.Mock()
    response.status_code = 401
    predicate = when.status(401) | when.raises(retry.BASE_CLIENT_EXCEPTION)

    # Verify: Calls __call__ for both predicates
    request_builder.client.exceptions.BaseClientException = RuntimeError
    predicate = predicate(request_builder)

    # Verify: when left predicate matches
    assert predicate.should_retry_after_response(response) is True

    # Verify: when right predicate matches
    assert (
        predicate.should_retry_after_exception(
            RuntimeError, RuntimeError(), None
        )
        is True
    )

    # Verify: when neither matches
    assert (
        predicate.should_retry_after_exception(Exception, Exception(), None)
        is False
    )


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
