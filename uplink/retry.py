# Standard library imports
import math

# Local imports
from uplink import decorators
from uplink.clients.io import RequestTemplate, transitions


def _clamp_generator(iterator, size):
    count = 0
    while size > count:
        yield next(iterator)
        count += 1


def _exponential_back_off(base=2, alpha=1, max_value=math.inf):
    exponent = 0
    while True:
        delay = alpha * base ** exponent
        yield min(delay, max_value)
        exponent += 1


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
    def __init__(self, max_attempts=5):
        self._max_attempts = max_attempts
        self._back_off_func = _exponential_back_off

    def modify_request(self, request_builder):
        request_builder.add_request_template(self._create_template())

    def _create_back_off_iterator(self):
        return _clamp_generator(self._back_off_func(), self._max_attempts - 1)

    def _create_template(self):
        return RetryTemplate(self._create_back_off_iterator(), lambda *_: True)
