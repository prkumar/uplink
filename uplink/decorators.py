# Standard library imports
import inspect

# Local imports
from uplink import exceptions, helpers, hooks, interfaces, types


__all__ = [
    "headers",
    "form_url_encoded",
    "multipart",
    "json",
    "timeout",
    "returns",
    "args",
    "response_handler",
    "error_handler",
    "inject",
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


class MethodAnnotationHandlerBuilder(interfaces.AnnotationHandlerBuilder):

    def __init__(self):
        self._method_annotations = list()

    def add_annotation(self, annotation, *args_, **kwargs):
        self._method_annotations.append(annotation)
        super(MethodAnnotationHandlerBuilder, self).add_annotation(annotation)
        return annotation

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
    def _is_static_call(cls, *args_, **kwargs):
        if super(MethodAnnotation, cls)._is_static_call(*args_, **kwargs):
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
                helpers.set_api_definition(class_or_builder, name, builder)
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
    """
    A decorator that adds static headers for API calls.

    .. code-block:: python

        @headers({"User-Agent": "Uplink-Sample-App})
        @get("/user")
        def get_user(self):
            \"""Get the current user\"""

    When used as a class decorator, :py:class:`headers` applies to
    all consumer methods bound to the class:

    .. code-block:: python

        @headers({"Accept": "application/vnd.github.v3.full+json")
        class GitHub(Consumer):
            ...

    :py:class:`headers` takes the same arguments as :py:class:`dict`.

    Args:
        *arg: A dict containing header values.
        **kwargs: More header values.
    """

    def __init__(self, arg, **kwargs):
        if isinstance(arg, str):
            key, value = self._get_header(arg)
            self._headers = {key: value}
        elif isinstance(arg, list):
            self._headers = dict(self._get_header(a) for a in arg)
        else:
            self._headers = dict(arg, **kwargs)

    def _get_header(self, arg):
        return map(str.strip, arg.split(":"))

    def modify_request(self, request_builder):
        """Updates header contents."""
        request_builder.info["headers"].update(self._headers)


# noinspection PyPep8Naming
class form_url_encoded(MethodAnnotation):
    """
    URL-encodes the request body.

    Used on POST/PUT/PATCH request. It url-encodes the body of the
    message and sets the appropriate ``Content-Type`` header. Further,
    each field argument should be annotated with
    :py:class:`uplink.Field`.

    Example:
        .. code-block:: python

            @form_url_encoded
            @post("/users/edit")
            def update_user(self, first_name: Field, last_name: Field):
                \"""Update the current user.\"""
    """
    _can_be_static = True

    # XXX: Let `requests` handle building urlencoded syntax.
    # def modify_request(self, request_builder):
    #     request_builder.info.headers(
    #         {"Content-Type": "application/x-www-form-urlencoded"}
    #     )


# noinspection PyPep8Naming
class multipart(MethodAnnotation):
    """
    Sends multipart form data.

    Multipart requests are commonly used to upload files to a server.
    Further, annotate each part argument with :py:class:`Part`.

    Example:

        .. code-block:: python

            @multipart
            @put(/user/photo")
            def update_user(self, photo: Part, description: Part):
                \"""Upload a user profile photo.\"""
    """
    _can_be_static = True

    # XXX: Let `requests` handle building multipart syntax.
    # def modify_request(self, request_builder):
    #     request_builder.info.headers(
    #         {"Content-Type": "multipart/form-data"}
    #     )


# noinspection PyPep8Naming
class json(MethodAnnotation):
    """Use as a decorator to make JSON requests.

    You should annotate a method argument with `uplink.Body` which
    indicates that the argument's value should become the request's
    body. :py:class:`uplink.Body` has to be either a dict or a subclass
    of py:class:`collections.Mapping`.

    Example:
        .. code-block:: python

            @json
            @patch(/user")
            def update_user(self, **info: Body):
                \"""Update the current user.\"""
    """
    _can_be_static = True

    def modify_request(self, request_builder):
        """Modifies JSON request."""
        try:
            request_builder.info["json"] = request_builder.info.pop("data")
        except KeyError:
            pass


# noinspection PyPep8Naming
class timeout(MethodAnnotation):
    """
    Time to wait for a server response before giving up.

    When used on other decorators it specifies how long (in secs) a
    decorator should wait before giving up.

    Example:
        .. code-block:: python

            @timeout(60)
            @get("/user/posts")
            def get_posts(self):
                \"""Fetch all posts for the current users.\"""

    When used as a class decorator, :py:class:`timeout` applies to all
    consumer methods bound to the class.

    Args:
        seconds (int): An integer used to indicate how long should the
            request wait.
    """
    def __init__(self, seconds):
        self._seconds = seconds

    def modify_request(self, request_builder):
        """Modifies request timeout."""
        request_builder.info["timeout"] = self._seconds


# noinspection PyPep8Naming
class returns(MethodAnnotation):
    """
    Specify the function's return annotation for Python 2.7
    compatibility.

    In Python 3, to provide a consumer method's return type, you can
    set the it as the method's return annotation:

    .. code-block:: python

        @get("/users/{username}")
        def get_user(self, username) -> UserSchema:
            \"""Get a specific user.\"""

    For Python 2.7 compatibility, you can use this decorator instead:

    .. code-block:: python

        @returns(UserSchema)
        @get("/users/{username}")
        def get_user(self, username):
            \"""Get a specific user.\"""
    """

    def __init__(self, type):
        self._type = type

    def modify_request(self, request_builder):
        request_builder.return_type = self._type


# noinspection PyPep8Naming
class args(MethodAnnotation):
    """
    Annotate method arguments for Python 2.7 compatibility.

    Arrange annotations in the same order as their corresponding
    function arguments.

    Example:
        .. code-block:: python

            @args(Path, Query)
            @get("/users/{username})
            def get_user(self, username, visibility):
                \"""Get a specific user.\"""

    Use keyword args to target specific method parameters.

    Example:
        .. code-block:: python

            @args(visibility=Query)
            @get("/users/{username})
            def get_user(self, username, visibility):
                \"""Get a specific user.\"""

    Args:
        *annotations: Any number of annotations.
        **more_annotations: More annotations, targeting specific method
           arguments.
    """
    def __init__(self, *annotations, **more_annotations):
        self._annotations = annotations
        self._more_annotations = more_annotations

    def __call__(self, obj):
        if inspect.isfunction(obj):
            handler = types.ArgumentAnnotationHandlerBuilder.from_func(obj)
            self._helper(handler)
            return obj
        else:
            return super(args, self).__call__(obj)

    def _helper(self, builder):
        builder.set_annotations(self._annotations, **self._more_annotations)

    def modify_request_definition(self, request_definition_builder):
        """Modifies dynamic requests with given annotations"""
        self._helper(request_definition_builder.argument_handler_builder)


class _InjectableMethodAnnotation(MethodAnnotation):
    def modify_request(self, request_builder):
        request_builder.add_transaction_hook(self)


# noinspection PyPep8Naming
class response_handler(_InjectableMethodAnnotation, hooks.ResponseHandler):
    """
    A decorator for creating custom response handlers.

    To register a function as a custom response handler, decorate the
    function with this class. The decorated function should accept a single
    positional argument, an HTTP response object:

    Example:
        .. code-block:: python

            @response_handler
            def raise_for_status(response):
                response.raise_for_status()
                return response

    Then, to apply custom response handling to a request method, simply
    decorate the method with the registered response handler:

    Example:
        .. code-block:: python

            @raise_for_status
            @get("/user/posts")
            def get_posts(self):
                \"""Fetch all posts for the current users.\"""

    To apply custom response handling on all request methods of a
    :py:class:`uplink.Consumer` subclass, simply decorate the class with
    the registered response handler:

    Example:
        .. code-block:: python

            @raise_for_status
            class GitHub(Consumer):
               ...

    .. versionadded:: 0.4.0
    """


# noinspection PyPep8Naming
class error_handler(_InjectableMethodAnnotation, hooks.ExceptionHandler):
    """
    A decorator for creating custom error handlers.

    To register a function as a custom error handler, decorate the
    function with this class. The decorated function should accept three
    positional arguments: (1) the type of the exception, (2) the
    exception instance raised, and (3) a traceback instance.

    Example:
        .. code-block:: python

            @error_handler
            def raise_api_error(exc_type, exc_val, exc_tb):
                # wrap client error with custom API error
                ...

    Then, to apply custom error handling to a request method, simply
    decorate the method with the registered error handler:

    Example:
        .. code-block:: python

            @raise_api_error
            @get("/user/posts")
            def get_posts(self):
                \"""Fetch all posts for the current users.\"""

    To apply custom error handling on all request methods of a
    :py:class:`uplink.Consumer` subclass, simply decorate the class with
    the registered error handler:

    Example:
        .. code-block:: python

            @raise_api_error
            class GitHub(Consumer):
               ...

    .. versionadded:: 0.4.0

    Note:
        Error handlers can not completely suppress exceptions. The
        original exception is thrown if the error handler doesn't throw
        anything.
    """


# noinspection PyPep8Naming
class inject(_InjectableMethodAnnotation, hooks.TransactionHookChain):
    """
    A decorator that applies one or more hooks to a request method.

    Example:
        .. code-block:: python

            @inject(Query("sort").with_value("pushed"))
            @get("users/{user}/repos")
            def list_repos(self, user):
                \"""Lists user's public repos by latest pushed.\"""

    .. versionadded:: 0.4.0
    """
