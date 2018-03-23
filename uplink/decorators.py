# Standard library imports
import collections
import functools
import inspect

# Local imports
from uplink import converters, helpers, hooks, interfaces, types

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


class MethodAnnotationHandlerBuilder(interfaces.AnnotationHandlerBuilder):

    def __init__(self):
        self._class_annotations = list()
        self._method_annotations = list()

    def add_annotation(self, annotation, *args_, **kwargs):
        if kwargs.get("is_class", False):
            self._class_annotations.append(annotation)
        else:
            self._method_annotations.append(annotation)
        super(MethodAnnotationHandlerBuilder, self).add_annotation(annotation)
        return annotation

    def build(self):
        return MethodAnnotationHandler(
            self._class_annotations + self._method_annotations
        )


class MethodAnnotationHandler(interfaces.AnnotationHandler):

    def __init__(self, method_annotations):
        self._method_annotations = list(method_annotations)

    @property
    def annotations(self):
        return iter(self._method_annotations)

    def handle_builder(self, request_builder):
        for annotation in self._method_annotations:
            annotation.modify_request(request_builder)


# TODO: Only decorate consumers
class MethodAnnotation(interfaces.Annotation):
    _http_method_blacklist = None
    _http_method_whitelist = None

    @staticmethod
    def _is_consumer_class(c):
        return inspect.isclass(c) and issubclass(c, interfaces.Consumer)

    @classmethod
    def supports_http_method(cls, method):
        method = method.upper()
        if cls._http_method_blacklist is not None:
            return method not in cls._http_method_blacklist
        if cls._http_method_whitelist is not None:
            return method in cls._http_method_whitelist
        return True

    @classmethod
    def _is_relevant_for_builder(cls, builder):
        return cls.supports_http_method(builder[1].method)

    @classmethod
    def _is_static_call(cls, *args_, **kwargs):
        if super(MethodAnnotation, cls)._is_static_call(*args_, **kwargs):
            return True
        try:
            is_consumer_class = cls._is_consumer_class(args_[0])
        except IndexError:
            return False
        else:
            return is_consumer_class and not (kwargs or args_[1:])

    def __call__(self, class_or_builder):
        if self._is_consumer_class(class_or_builder):
            builders = helpers.get_api_definitions(class_or_builder)
            builders = filter(self._is_relevant_for_builder, builders)

            for name, b in builders:
                b.method_handler_builder.add_annotation(self, is_class=True)
                helpers.set_api_definition(class_or_builder, name, b)
        elif isinstance(class_or_builder, interfaces.RequestDefinitionBuilder):
            class_or_builder.method_handler_builder.add_annotation(self)
        return class_or_builder

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
    _http_method_blacklist = {"GET"}
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
    _http_method_blacklist = {"GET"}
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
    _http_method_blacklist = {"GET"}
    _can_be_static = True

    @staticmethod
    def _sequence_path_resolver(path, value, body):
        if not path:
            raise ValueError("Path sequence cannot be empty.")
        for name in path[:-1]:
            body = body.setdefault(name, {})
            if not isinstance(body, collections.Mapping):
                raise ValueError(
                    "Failed to set nested JSON attribute '%s': "
                    "parent field '%s' is not a JSON object."
                    % (path, name)
                )
        body[path[-1]] = value

    class _JsonBody(collections.MutableMapping):
        """
        A helper class that builds a JSON request body using a
        dictionary interface.

        Fields that are built using a field annotation
        """

        def __init__(self):
            self._body = {}

        def __setitem__(self, path, value):
            if isinstance(path, tuple):
                json._sequence_path_resolver(path, value, self._body)
            else:
                self._body[path] = value

        def __delitem__(self, key):
            del self._body[key]

        def __getitem__(self, key):
            return self._body[key]

        def __len__(self):
            return len(self._body)

        def __iter__(self):
            return iter(self._body)

    def modify_request(self, request_builder):
        """Modifies JSON request."""
        old_body = request_builder.info.pop("data", {})
        request_builder.info["json"] = self._JsonBody()
        request_builder.info["json"].update(old_body)


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

    List = converters.TypingConverter.List
    """
    .. versionadded:: v0.5.0
    
    A proxy for :py:class:`typing.List` that is safe to use in type 
    hints with Python 3.4 and below.

    .. code-block:: python

        @returns.json
        @get("/users")
        def get_users(self) -> returns.List[str]:
            \"""Fetches all users\"""
    """

    Dict = converters.TypingConverter.Dict
    """
    .. versionadded:: v0.5.0
    
    A proxy for :py:class:`typing.Dict` that is safe to use in type 
    hints with Python 3.4 and below

    .. code-block:: python

        @returns.json
        @get("/users")
        def get_users(self) -> returns.Dict[str, str]:
            \"""Fetches all users\"""
    """

    class Json(converters.interfaces.Converter):
        # TODO: Support JSON Pointer (https://tools.ietf.org/html/rfc6901)

        def __init__(self, model, member=()):
            self._model = model
            self._model_converter = None

            if not isinstance(member, (list, tuple)):
                member = (member,)
            self._member = member

        def set_chain(self, chain):
            self._model_converter = chain(self._model)

        def convert(self, response):
            content = response.json()
            for name in self._member:
                content = content[name]
            if self._model_converter is not None:
                content = self._model_converter(content)
            return content

    # noinspection PyPep8Naming
    class json(MethodAnnotation):
        """
        .. versionadded:: v0.5.0

        Specifies that the decorated consumer method should return a
        JSON object.

        Example:

            .. code-block:: python

                @returns.json
                @get("/users/{username}")
                def get_user(self, username):
                    \"""Get a specific user.\"""


        Returning a Specific JSON Field:

            This decorator accepts two optional arguments. The
            :py:attr:`member` argument accepts a string or tuple that
            specifies the path of an internal field in the JSON
            document.

            For instance, consider an API that returns JSON responses
            that, at the root of the document, contains both the
            server-retrieved data and a list of relevant API errors:

            .. code-block:: json
                :emphasize-lines: 2

                {
                    "data": { "user": "prkumar", "id": 10432 }
                    "errors": []
                }

            If returning the list of errors is unnecessary, we can use
            the :py:attr:`member` argument to strictly return the inner
            field :py:attr:`data`:

            .. code-block:: python

                @returns.json(member="data")
                @get("/users/{username}")
                def get_user(self, username):
                    \"""Get a specific user.\"""

        Deserialize Objects from JSON:

            Often, JSON responses represent models in your application.
            If an existing Python object encapsulates this model, use
            the :py:attr:`model` argument to specify it as the return
            type:

            .. code-block:: python

                @returns.json(model=User, member="data")
                @get("/users/{username}")
                def get_user(self, username):
                    \"""Get a specific user.\"""

            This pattern typically requires also registering a converter
            that knows how to deserialize the JSON into your data model
            object or leveraging a built-in converter (e.g.,
            :py:class:`uplink.converters.MarshmallowConverter`).

            For Python 3 users, you can alternatively provide a return
            value annotation. Hence, the previous code is equivalent
            to the following in Python 3:

            .. code-block:: python

                @returns.json(member="data")
                @get("/users/{username}")
                def get_user(self, username) -> User:
                    \"""Get a specific user.\"""

        """
        _can_be_static = True

        def __init__(self, model=None, member=()):
            self._model = model
            self._member = member

        def modify_request(self, request_builder):
            return_type = request_builder.return_type
            return_type = self._model if return_type is None else return_type
            request_builder.return_type = returns.Json(
                return_type, self._member
            )


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


class _BaseHandlerAnnotation(_InjectableMethodAnnotation):
    def __init__(self, func):
        functools.update_wrapper(self, func)


# noinspection PyPep8Naming
class response_handler(_BaseHandlerAnnotation, hooks.ResponseHandler):
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
class error_handler(_BaseHandlerAnnotation, hooks.ExceptionHandler):
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
