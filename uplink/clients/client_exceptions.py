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
register their exceptions and involves dynamically appending a proxy
exception to each registered exception's class hierarchy. This makes
the proxy a direct superclass of the client exception and renders the
desired behavior by conventional polymorphism.
"""


class _ClientException(BaseException):
    # Inherit BaseException instead of Exception so Python can create a
    # consistent method resolution order when dynamically adding this
    # class to the class hierarchy.

    @classmethod
    def register(cls, exc_cls):
        exc_cls.__bases__ += (cls,)


class BaseClientException(_ClientException):
    """Base class for client errors."""


class ConnectionError(_ClientException):
    """A connection error occurred."""


class Timeout(_ClientException):
    """The request timed out."""


class SSLError(_ClientException):
    """An SSL error occurred."""


class InvalidURL(_ClientException):
    """The URL provided was somehow invalid."""
