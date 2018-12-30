
__all__ = ["after_attempts"]


class _AfterAttemptStopper(object):
    def __init__(self, num):
        self._num = num
        self._attempt = 0

    def __call__(self, *_):
        self._attempt += 1
        return self._num <= self._attempt


def after_attempts(attempts):
    """Stops retrying after the specified number of ``attempts``."""
    return lambda: _AfterAttemptStopper(attempts)


class _DisableStop(object):
    def __call__(self, *args, **kwargs):
        return False


DISABLE = _DisableStop()
"""Continuously retry until a response is rendered."""
