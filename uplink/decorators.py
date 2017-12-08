# Standard library imports
import inspect

# Local imports
from uplink import exceptions, helpers, interfaces


__all__ = [
    "headers",
    "form_url_encoded",
    "multipart",
    "json",
    "timeout",
    "returns",
    "args"
]


class HttpMethodNotSupport(exceptions.AnnotationError):
    message = (
        "Error on method `%s`: annotation %s is not supported with %s "
        "commands."
    )

    def __init__(self, request_definition_builder, annotation):
        self.message = self.message % (
            request_definition_builder.__name__,
            type(annotation),
            request_definition_builder.method.upper()
        )


class MethodAnnotationHandlerBuilder(
    interfaces.AnnotationHandlerBuilder
):

    def __init__(self):
        self._method_annotations = list()

    def add_annotation(self, annotation, *args_, **kwargs):
        super(MethodAnnotationHandlerBuilder, self).add_annotation(annotation)
        self._method_annotations.append(annotation)

    def build(self):
        return MethodAnnotationHandler(self._method_annotations)


class MethodAnnotationHandler(interfaces.AnnotationHandler):

    def __init__(self, method_annotations):
        self._method_annotations = list(method_annotations)

    @property
    def annotations(self):
        return iter(self._method_annotations)

    def handle_builder(self, request_builder):
        for annotation in self._method_annotations:
            annotation.modify_request(request_builder)


class MethodAnnotation(interfaces.Annotation):
    http_method_whitelist = None

    @classmethod
    def is_static_call(cls, *args_, **kwargs):
        if super(MethodAnnotation, cls).is_static_call(*args_, **kwargs):
            return True
        try:
            is_class = inspect.isclass(args_[0])
        except IndexError:
            return False
        else:
            return is_class and not (kwargs or args_[1:])

    def __call__(self, class_or_builder):
        if inspect.isclass(class_or_builder):
            builders = helpers.get_api_definitions(class_or_builder)
            for name, builder in builders:
                builder.method_handler_builder.add_annotation(self)
                setattr(class_or_builder, name, builder)
        else:
            class_or_builder.method_handler_builder.add_annotation(self)
        return class_or_builder

    def modify_request_definition(self, request_definition_builder):
        if self.http_method_whitelist is not None:
            method = request_definition_builder.method.upper()
            if method not in self.http_method_whitelist:
                raise HttpMethodNotSupport(request_definition_builder, self)

    def modify_request(self, request_builder):
        pass


# noinspection PyPep8Naming
class headers(MethodAnnotation):
    """Use as a decorator on a class to add Headers to all API calls.

    Args:
        arg: A dict containing header input parameters
        kwargs: A dict containing header input parameters
    """

    def __init__(self, arg, **kwargs):
        # TODO: allow the first argument to be a list or str, in
        # which case you would split the strings by a colon delimiter
        # to identify the headers.
        self._headers = dict(arg, **kwargs)

    def modify_request(self, request_builder):
        """Updates header contents."""
        request_builder.info["headers"].update(self._headers)


# noinspection PyPep8Naming
class form_url_encoded(MethodAnnotation):
    """URL-encodes the request body.

    Used on POST/PUT/PATCH request. It url-encodes the body of the message
    and sets the header to: `Content-Type:application/x-www-form-urlencoded`

    Attributes:
        can_be_static: A boolean value indicating that this annotation can be
            used as a decorator without any arguments passed.
    """
    can_be_static = True

    # XXX: Let `requests` handle building urlencoded syntax.
    # def modify_request(self, request_builder):
    #     request_builder.info.headers(
    #         {"Content-Type": "application/x-www-form-urlencoded"}
    #     )


# noinspection PyPep8Naming
class multipart(MethodAnnotation):
    """Sends multipart form data.

    Multipart requests are commonly used to upload files to a server.

    Attributes:
        can_be_static: A boolean value indicating that this annotation can be
            used as a decorator without any arguments passed.
    """
    can_be_static = True

    # XXX: Let `requests` handle building multipart syntax.
    # def modify_request(self, request_builder):
    #     request_builder.info.headers(
    #         {"Content-Type": "multipart/form-data"}
    #     )


# noinspection PyPep8Naming
class json(MethodAnnotation):
    """Use as a decorator to make JSON requests.

    You should annotate a method argument with `uplink.Body` which indicates
    that the argument's value should become the request's body.
    `uplink.Body` has to be either a dict or a subclass of
    `collections.Mapping`.

    Attributes:
        can_be_static: A boolean value indicating that this annotation can be
            used as a decorator without any arguments passed.
    """
    can_be_static = True

    def modify_request(self, request_builder):
        """Modifies JSON request."""
        try:
            request_builder.info["json"] = request_builder.info.pop("data")
        except KeyError:
            pass


# noinspection PyPep8Naming
class timeout(MethodAnnotation):
    """Time to wait for a server response before giving up.

    When used on other decorators it specifies how long (in secs)
    a decorator should wait before giving up.

    Args:
        seconds: An integer used to indicate how long should the
            request wait.
    """
    def __init__(self, seconds):
        self._seconds = seconds

    def modify_request(self, request_builder):
        """Modifies request timeout."""
        request_builder.info["timeout"] = self._seconds


# noinspection PyPep8Naming
class returns(MethodAnnotation):
    def __init__(self, type):
        self._type = type

    def modify_request(self, request_builder):
        request_builder.set_return_type(self._type)


# noinspection PyPep8Naming
class args(MethodAnnotation):
    """Handles dynamic requests by using method annotations.

    Arranges annotations in the same order as their
    corresponding function arguments.

    Args:
        *annotations: Any number of function arguments
        **more_annotations: Any number of function arguments
    """
    def __init__(self, *annotations, **more_annotations):
        self._annotations = annotations
        self._more_annotations = more_annotations

    def modify_request_definition(self, request_definition_builder):
        """Modifies dynamic requests with given annotations"""
        request_definition_builder.argument_handler_builder.set_annotations(
            self._annotations, **self._more_annotations
        )
