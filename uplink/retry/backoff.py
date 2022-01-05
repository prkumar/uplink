# Standard imports
import random
import sys

# Constants
MAX_VALUE = sys.maxsize / 2

__all__ = ["jittered", "exponential", "fixed"]


class RetryBackoff(object):
    def after_response(self, request, response):
        raise NotImplementedError  # pragma: no cover

    def after_exception(self, request, exc_type, exc_val, exc_tb):
        raise NotImplementedError  # pragma: no cover

    def after_stop(self):
        pass  # pragma: no cover


class IterableBackoff(RetryBackoff):
    def __init__(self):
        self.__iterator = None

    def __iter__(self):
        raise NotImplementedError  # pragma: no cover

    def __call__(self):
        return iter(self)

    def __next(self):
        if self.__iterator is None:
            self.__iterator = iter(self)

        try:
            return next(self.__iterator)
        except StopIteration:
            return None

    def after_response(self, request, response):
        return self.__next()

    def after_exception(self, request, exc_type, exc_val, exc_tb):
        return self.__next()

    def after_stop(self):
        self.__iterator = None


class jittered(IterableBackoff):
    def __init__(self, base=2, multiplier=1, minimum=0, maximum=MAX_VALUE):
        super().__init__()
        self._exp_backoff = exponential(base, multiplier, minimum, maximum)

    def __iter__(self):
        return (random.uniform(0, 1) * delay for delay in self._exp_backoff())


class exponential(IterableBackoff):
    def __init__(self, base=2, multiplier=1, minimum=0, maximum=MAX_VALUE):
        super().__init__()
        self._base = base
        self._multiplier = multiplier
        self._minimum = minimum
        self._maximum = maximum

    def __iter__(self):
        delay = self._multiplier
        while self._minimum > delay:
            delay *= self._base
        while True:
            yield min(delay, self._maximum)
            delay *= self._base


class fixed(IterableBackoff):
    def __init__(self, seconds):
        super().__init__()
        self._seconds = seconds

    def __iter__(self):
        while True:
            yield self._seconds
