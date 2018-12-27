# Local imports
from uplink import retry


def test_exponential_backoff_minimum():
    backoff = retry.exponential_backoff(minimum=8)()
    assert next(backoff) == 8
    assert next(backoff) == 16


def test_retry_stop_default():
    decorator = retry()
    assert retry.stop_never == decorator.stop


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
