class _UnmappedClientException(BaseException):
    pass


class Exceptions(object):
    BaseClientException = _UnmappedClientException
    """Base class for client errors."""

    ConnectionError = _UnmappedClientException
    """A connection error occurred."""

    Timeout = _UnmappedClientException
    """The request timed out."""

    SSLError = _UnmappedClientException
    """An SSL error occurred."""

    InvalidURL = _UnmappedClientException
    """The URL provided was somehow invalid."""
