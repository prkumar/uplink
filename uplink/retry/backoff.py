# Standard imports
import random
import sys

# Constants
MAX_VALUE = sys.maxsize / 2

__all__ = ["jittered", "exponential", "fixed"]


def jittered(base=2, multiplier=1, minimum=0, maximum=MAX_VALUE):
    """
    Waits using capped exponential backoff and full jitter.

    The implementation is discussed in `this AWS Architecture Blog
    post <https://amzn.to/2xc2nK2>`_, which recommends this approach
    for any remote clients, as it minimizes the total completion
    time of competing clients in a distributed system experiencing
    high contention.
    """
    exp_backoff = exponential(base, multiplier, minimum, maximum)
    return lambda *_: iter(
        random.uniform(0, 1) * delay for delay in exp_backoff()
    )  # pragma: no cover


def exponential(base=2, multiplier=1, minimum=0, maximum=MAX_VALUE):
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


def fixed(seconds):
    """Waits for a fixed number of ``seconds`` before each retry."""

    def wait_iterator():
        while True:
            yield seconds

    return wait_iterator
