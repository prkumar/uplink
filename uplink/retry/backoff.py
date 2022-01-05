# Standard imports
import random
import sys

# Constants
MAX_VALUE = sys.maxsize / 2

__all__ = ["jittered", "exponential", "fixed"]


class RetryBackoff(object):
    """
    Base class for strategies that calculate the amount of time to wait
    between retry attempts.
    """

    def after_response(self, request, response):
        """
        Returns the number of seconds to wait before retrying the
        request, or None to indicate that the given response should
        be returned.
        """
        raise NotImplementedError  # pragma: no cover

    def after_exception(self, request, exc_type, exc_val, exc_tb):
        """
        Returns the number of seconds to wait before retrying the
        request, or None to indicate that the given exception should be
        raised.
        """
        raise NotImplementedError  # pragma: no cover

    def after_stop(self):
        """
        Handles any clean-up necessary following the final retry
        attempt.
        """
        pass  # pragma: no cover


class IterableBackoff(RetryBackoff):
    """
    Base class for creating retry strategies from an iterable that
    emits an ordered sequence of timeouts.
    """

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
        """
        Waits using capped exponential backoff and full jitter.

        The implementation is discussed in `this AWS Architecture Blog
        post <https://amzn.to/2xc2nK2>`_, which recommends this approach
        for any remote clients, as it minimizes the total completion
        time of competing clients in a distributed system experiencing
        high contention.
        """
        super().__init__()
        self._exp_backoff = exponential(base, multiplier, minimum, maximum)

    def __iter__(self):
        return (random.uniform(0, 1) * delay for delay in self._exp_backoff())


class exponential(IterableBackoff):
    def __init__(self, base=2, multiplier=1, minimum=0, maximum=MAX_VALUE):
        """
        Waits using capped exponential backoff, meaning that the delay
        is multiplied by a constant ``base`` after each attempt, up to
        an optional ``maximum`` value.
        """
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
        """Waits for a fixed number of ``seconds`` before each retry."""
        super().__init__()
        self._seconds = seconds

    def __iter__(self):
        while True:
            yield self._seconds
