class _ClientExceptionFlag(object):
    def __init__(self):
        self._exception_classes = ()

    def register(self, *exception_classes):
        self._exception_classes += exception_classes

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return self._exception_classes


class ClientExceptions(object):
    # The goal here is to provide end-users with a way to catch client
    # exceptions in an agnostic manner.
    #
    # The initial plan was to define some common exception classes, then
    # have client writers register the appropriate client-specific
    # exceptions as virtual subclasses (similar to abc.ABCMeta).
    # See: https://github.com/prkumar/uplink/issues/57#issuecomment-362421400
    #
    # However, that wouldn't work because when determining if a thrown
    # exception should be caught, Python does an explicit subtype check,
    # bypassing any special subclass checks we can define (e.g.,
    # __subclasscheck__).
    # See: https://stackoverflow.com/a/23891850

    #: Base class for client errors.
    BaseException = _ClientExceptionFlag()

    #: A connection error occurred.
    ConnectionError = _ClientExceptionFlag()

    #: The request timed out.
    TimeoutError = _ClientExceptionFlag()

    #: An SSL error occurred.
    SSLError = _ClientExceptionFlag()

    #: The URL provided was somehow invalid
    InvalidURL = _ClientExceptionFlag()


#: Class for accessing HTTP client exceptions in an agnostic manner.
client_exceptions = ClientExceptions()
