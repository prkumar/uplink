class Error(Exception):
    """Base exception for this package"""
    message = None

    def __str__(self):
        return str(self.message)


class UplinkBuilderError(Error):
    """Something went wrong while building a service."""
    message = "`%s`: %s"

    def __init__(self, service_cls, definition_name, error):
        fullname = service_cls.__name__ + "." + definition_name
        self.message = self.message % (fullname, error)
        self.error = error


class InvalidRequestDefinition(Error):
    """Something went wrong when building the request definition."""


class AnnotationError(Error):
    """Something went wrong with an annotation."""

