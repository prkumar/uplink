"""
This module defines proxy exceptions that enable end-users to catch
client exceptions in an agnostic manner.

The initial plan was to define some common exception classes, then have
client writers register the appropriate client-specific exceptions as
virtual subclasses (similar to abc.ABCMeta).

However, that approach fails because, when determining if a thrown
exception should be caught, Python does an explicit subtype check,
bypassing any special subclass checks we can define (e.g.,
__subclasscheck__). See: https://stackoverflow.com/a/23891850

The workaround employed here maintains the need for client writers to
register their exceptions. For each registered exception, we generate a
subclass that is a child of both the client exception and the proxy
exception to which the writer registered it.

The client exception handling layer attempts to exchange client-raised
error, the layer attempts to exchange the client error for a subclass
generated in the previous step. If the exchange is successfully,
end-users can catch the subclass exception using either the proxy
exception or the original exception.
"""


# Inherit BaseException instead of Exception so Python can create a
# consistent method resolution order when we construct a subclass at
# runtime (see ClientException.__create_subclass)
class ClientException(BaseException):
    _registered_exceptions = {}

    @classmethod
    def _create_subclass(cls, exc_class):
        return type(exc_class.__name__, (exc_class, cls), {})

    @classmethod
    def register(cls, exc_cls):
        cls._registered_exceptions[exc_cls] = cls._create_subclass(exc_cls)

    @classmethod
    def wrap_exception_if_necessary(cls, exc_type, exc_val):
        """
        Attempts to exchange the given exception type and value for
        a proxy exception.
        """
        try:
            derived_class = cls._registered_exceptions[exc_type]
        except KeyError:
            return exc_type, exc_val
        else:
            wrapper = derived_class.__new__(derived_class)
            wrapper.__dict__ = exc_val.__dict__
            return derived_class, wrapper


class BaseClientException(ClientException):
    """Base class for client errors."""


class ConnectionError(BaseClientException):
    """A connection error occurred."""


class Timeout(ConnectionError):
    """The request timed out."""


class SSLError(ConnectionError):
    """An SSL error occurred."""


class InvalidURL(ClientException):
    """The URL provided was somehow invalid."""
