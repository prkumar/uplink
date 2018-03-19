"""
This module implements the built-in argument annotations and their
handling classes.
"""
# Standard library imports
import collections
import functools
import inspect

# Local imports
from uplink import compat, exceptions, hooks, interfaces
from uplink.converters import keys

__all__ = [
    "Path",
    "Query",
    "QueryMap",
    "Header",
    "HeaderMap",
    "Field",
    "FieldMap",
    "Part",
    "PartMap",
    "Body",
    "Url"
]


class ExhaustedArguments(exceptions.AnnotationError):
    message = (
        "Failed to add `%s` to method `%s`, as all arguments have "
        "been annotated."
    )

    def __init__(self, annotation, func):
        self.message = self.message % (annotation, func.__name__)


class ArgumentNotFound(exceptions.AnnotationError):
    message = "`%s` does not match any argument name of method `%s`."

    def __init__(self, name, func):
        self.message = self.message % (name, func.__name__)


class ArgumentAnnotationHandlerBuilder(interfaces.AnnotationHandlerBuilder):
    __ANNOTATION_BUILDER_KEY = "#ANNOTATION_BUILDER_KEY#"

    @classmethod
    def from_func(cls, func):
        if not hasattr(func, cls.__ANNOTATION_BUILDER_KEY):
            spec = compat.get_arg_spec(func)
            handler = cls(func, spec.args)
            setattr(func, cls.__ANNOTATION_BUILDER_KEY, handler)
            handler.add_annotations_from_spec(spec)
        return getattr(func, cls.__ANNOTATION_BUILDER_KEY)

    def __init__(self, func, arguments, func_is_method=True):
        self._arguments = arguments[func_is_method:]
        self._argument_types = collections.OrderedDict.fromkeys(self._arguments)
        self._defined = 0
        self._func = func

    def add_annotations_from_spec(self, spec):
        if spec.args:
            # Ignore `self` instance reference
            spec.annotations.pop(spec.args[0], None)
        self.set_annotations(spec.annotations)

    @property
    def missing_arguments(self):
        return (a for a in self._arguments if self._argument_types[a] is None)

    @property
    def remaining_args_count(self):
        return len(self._arguments) - self._defined

    def set_annotations(self, annotations=None, **more_annotations):
        if annotations is not None:
            if not isinstance(annotations, collections.Mapping):
                missing = tuple(
                    a for a in self.missing_arguments
                    if a not in more_annotations
                )
                annotations = dict(zip(missing, annotations))
            more_annotations.update(annotations)
        for name in more_annotations:
            self.add_annotation(more_annotations[name], name)

    def add_annotation(self, annotation, name=None, *args, **kwargs):
        try:
            name = next(self.missing_arguments) if name is None else name
        except StopIteration:
            raise ExhaustedArguments(annotation, self._func)
        if name not in self._argument_types:
            raise ArgumentNotFound(name, self._func)
        if inspect.isclass(annotation):
            annotation = annotation()
        if isinstance(annotation, NamedArgument) and annotation.name is None:
            annotation.name = name
        super(ArgumentAnnotationHandlerBuilder, self).add_annotation(annotation)
        self._defined += self._argument_types[name] is None
        self._argument_types[name] = annotation
        return annotation

    def is_done(self):
        return self.remaining_args_count == 0

    @property
    def _types(self):
        types = self._argument_types
        return ((k, types[k]) for k in types if types[k] is not None)

    def build(self):
        return ArgumentAnnotationHandler(
            self._func,
            collections.OrderedDict(self._types)
        )


class ArgumentAnnotationHandler(interfaces.AnnotationHandler):

    def __init__(self, func, arguments):
        self._func = func
        self._arguments = arguments

    @property
    def annotations(self):
        return iter(self._arguments.values())

    def get_relevant_arguments(self, call_args):
        annotations = self._arguments
        return ((n, annotations[n]) for n in call_args if n in annotations)

    def handle_call(self, request_builder, args, kwargs):
        call_args = compat.get_call_args(self._func, None, *args, **kwargs)
        self.handle_call_args(request_builder, call_args)

    def handle_call_args(self, request_builder, call_args):
        # TODO: Catch Annotation errors and chain them here + provide context.
        for name, annotation in self.get_relevant_arguments(call_args):
            annotation.modify_request(request_builder, call_args[name])


class ArgumentAnnotation(interfaces.Annotation):
    _can_be_static = True

    def __call__(self, request_definition_builder):
        request_definition_builder.argument_handler_builder.add_annotation(self)
        return request_definition_builder

    def _modify_request(self, request_builder, value):  # pragma: no cover
        pass

    @property
    def type(self):  # pragma: no cover
        return None

    @property
    def converter_key(self):  # pragma: no cover
        raise NotImplementedError

    def modify_request(self, request_builder, value):
        argument_type, converter_key = self.type, self.converter_key
        converter = request_builder.get_converter(converter_key, argument_type)
        value = converter.convert(value)
        self._modify_request(request_builder, value)


class TypedArgument(ArgumentAnnotation):

    def __init__(self, type=None):
        self._type = type

    @property
    def type(self):
        return self._type

    @property
    def converter_key(self):  # pragma: no cover
        raise NotImplementedError


class NamedArgument(TypedArgument):
    _can_be_static = True

    def __init__(self, name=None, type=None):
        self._arg_name = name
        super(NamedArgument, self).__init__(type)

    @property
    def name(self):
        return self._arg_name

    @name.setter
    def name(self, name):
        if self._arg_name is None:
            self._arg_name = name
        else:
            raise AttributeError("Name is already set.")
    
    @property
    def converter_key(self):  # pragma: no cover
        raise NotImplementedError


class FuncDecoratorMixin(object):
    @classmethod
    def _is_static_call(cls, *args_, **kwargs):
        if super(FuncDecoratorMixin, cls)._is_static_call(*args_, **kwargs):
            return True
        try:
            is_func = inspect.isfunction(args_[0])
        except IndexError:
            return False
        else:
            return is_func and not (kwargs or args_[1:])

    def __call__(self, obj):
        if inspect.isfunction(obj):
            ArgumentAnnotationHandlerBuilder.from_func(obj).add_annotation(self)
            return obj
        else:
            return super(FuncDecoratorMixin, self).__call__(obj)

    def with_value(self, value):
        """
        Creates an object that can be used with the
        :py:class:`Consumer._inject` method or
        :py:class:`~uplink.inject` decorator to inject request properties
        with specific values.

        .. versionadded:: 0.4.0
        """
        auditor = functools.partial(self.modify_request, value=value)
        return hooks.RequestAuditor(auditor)


class Path(NamedArgument):
    """
    Substitution of a path variable in a `URI template
    <https://tools.ietf.org/html/rfc6570>`__.

    URI template parameters are enclosed in braces (e.g.,
    :code:`{name}`). To map an argument to a declared URI parameter, use
    the :py:class:`Path` annotation:

    .. code-block:: python

        class TodoService(object):
            @get("/todos{/id}")
            def get_todo(self, todo_id: Path("id")): pass

    Then, invoking :code:`get_todo` with a consumer instance:

    .. code-block:: python

        todo_service.get_todo(100)

    creates an HTTP request with a URL ending in :code:`/todos/100`.

    Note:
        Any unannotated function argument that shares a name with a URL path
        parameter is implicitly annotated with this class at runtime.

        For example, we could simplify the method from the previous
        example by matching the path variable and method argument names:

        .. code-block:: python

            @get("/todos{/id}")
            def get_todo(self, id): pass
    """

    @property
    def converter_key(self):
        return keys.CONVERT_TO_STRING

    def modify_request_definition(self, request_definition_builder):
        request_definition_builder.uri.add_variable(self.name)

    def _modify_request(self, request_builder, value):
        request_builder.url.set_variable({self.name: value})


class Query(FuncDecoratorMixin, NamedArgument):
    """
    Set a dynamic query parameter.

    This annotation turns argument values into URL query
    parameters. You can include it as function argument
    annotation, in the format: ``<query argument>: uplink.Query``.

    If the API endpoint you are trying to query uses ``q`` as a query
    parameter, you can add ``q: uplink.Query`` to the consumer method to
    set the ``q`` search term at runtime.

    Example:
        .. code-block:: python

            @get("/search/commits")
            def search(self, search_term: Query("q")):
                '''Search all commits with the given search term.'''

        To specify whether or not the query parameter is already URL encoded,
        use the optional :py:obj:`encoded` argument:

        .. code-block:: python

            @get("/search/commits")
            def search(self, search_term: Query("q", encoded=True)):
                \"""Search all commits with the given search term.\"""

    Args:
        encoded (:obj:`bool`, optional): Specifies whether the parameter
            :py:obj:`name` and value are already URL encoded.
    """

    class QueryStringEncodingError(exceptions.AnnotationError):
        message = (
            "Failed to join encoded and unencoded query parameters."
        )

    def __init__(self, name=None, encoded=False, type=None):
        super(Query, self).__init__(name, type)
        self._encoded = encoded

    @staticmethod
    def _update_params(info, existing, new_params, encoded):
        # TODO: Consider moving some of this to the client backend.
        if encoded:
            params = [] if existing is None else [str(existing)]
            params.extend("%s=%s" % (n, new_params[n]) for n in new_params)
            info["params"] = "&".join(params)
        else:
            info["params"].update(new_params)

    @staticmethod
    def update_params(info, new_params, encoded):
        existing = info.setdefault("params", None if encoded else dict())
        if encoded == isinstance(existing, collections.Mapping):
            raise Query.QueryStringEncodingError()
        Query._update_params(info, existing, new_params, encoded)

    @property
    def converter_key(self):
        """Converts query parameters to the request body."""
        if self._encoded:
            return keys.CONVERT_TO_STRING
        else:
            return keys.Sequence(keys.CONVERT_TO_STRING)

    def _modify_request(self, request_builder, value):
        """Updates request body with the query parameter."""
        self.update_params(
            request_builder.info,
            {self.name: value},
            self._encoded
        )


class QueryMap(FuncDecoratorMixin, TypedArgument):
    """
    A mapping of query arguments.

    If the API you are using accepts multiple query arguments, you can
    include them all in your function method by using the format:
    ``<query argument>: uplink.QueryMap``

    Example:
        .. code-block:: python

            @get("/search/users")
            def search(self, **params: QueryMap):
                \"""Search all users.\"""

    Args:
        encoded (:obj:`bool`, optional): Specifies whether the parameter
            :py:obj:`name` and value are already URL encoded.
    """
    
    def __init__(self, encoded=False, type=None):
        super(QueryMap, self).__init__(type)
        self._encoded = encoded

    @property
    def converter_key(self):
        """Converts query mapping to request body."""
        if self._encoded:
            return keys.Map(keys.CONVERT_TO_STRING)
        else:
            return keys.Map(keys.Sequence(keys.CONVERT_TO_STRING))

    def _modify_request(self, request_builder, value):
        """Updates request body with the mapping of query args."""
        Query.update_params(request_builder.info, value, self._encoded)


class Header(FuncDecoratorMixin, NamedArgument):
    """
    Pass a header as a method argument at runtime.

    While :py:class:`uplink.headers` attaches static headers
    that define all requests sent from a consumer method, this
    class turns a method argument into a dynamic header value.

    Example:
        .. code-block:: python

            @get("/user")
            def (self, session_id: Header("Authorization")):
                \"""Get the authenticated user\"""
    """

    @property
    def converter_key(self):
        """Converts passed argument to string."""
        return keys.CONVERT_TO_STRING

    def _modify_request(self, request_builder, value):
        """Updates request header contents."""
        request_builder.info["headers"][self.name] = value


class HeaderMap(FuncDecoratorMixin, TypedArgument):
    """Pass a mapping of header fields at runtime."""

    @property
    def converter_key(self):
        """Converts every header field to string"""
        return keys.Map(keys.CONVERT_TO_STRING)

    @classmethod
    def _modify_request(cls, request_builder, value):
        """Updates request header contents."""
        request_builder.info["headers"].update(value)


class Field(NamedArgument):
    """
    Defines a form field to the request body.

    Use together with the decorator :py:class:`uplink.form_url_encoded`
    and annotate each argument accepting a form field with
    :py:class:`uplink.Field`.

    Example::
        .. code-block:: python

            @form_url_encoded
            @post("/users/edit")
            def update_user(self, first_name: Field, last_name: Field):
                \"""Update the current user.\"""
    """

    class FieldAssignmentFailed(exceptions.AnnotationError):
        """Used if the field chosen failed to be defined."""
        message = (
            "Failed to define field '%s' to request body. Another argument "
            "annotation might have overwritten the body entirely."
        )

        def __init__(self, field):
            self.message = self.message % field.name

    @property
    def converter_key(self):
        """Converts type to string."""
        return keys.CONVERT_TO_STRING

    def _modify_request(self, request_builder, value):
        """Updates the request body with chosen field."""
        try:
            request_builder.info["data"][self.name] = value
        except TypeError:
            # TODO: re-raise with TypeError
            # `data` does not support item assignment
            raise self.FieldAssignmentFailed(self)


class FieldMap(TypedArgument):
    """
    Defines a mapping of form fields to the request body.

    Use together with the decorator :py:class:`uplink.form_url_encoded`
    and annotate each argument accepting a form field with
    :py:class:`uplink.FieldMap`.

    Example:
        .. code-block:: python

            @form_url_encoded
            @post("/user/edit")
            def create_post(self, **user_info: FieldMap):
                \"""Update the current user.\"""
    """

    class FieldMapUpdateFailed(exceptions.AnnotationError):
        """Use when the attempt to update the request body failed."""
        message = (
            "Failed to update request body with field map. Another argument "
            "annotation might have overwritten the body entirely."
        )

    @property
    def converter_key(self):
        """Converts type to string."""
        return keys.Map(keys.CONVERT_TO_STRING)

    def _modify_request(self, request_builder, value):
        """Updates request body with chosen field mapping."""
        try:
            request_builder.info["data"].update(value)
        except AttributeError:
            # TODO: re-raise with AttributeError
            raise self.FieldMapUpdateFailed()


class Part(NamedArgument):
    """
    Marks an argument as a form part.

    Use together with the decorator :py:class:`uplink.multipart` and
    annotate each form part with :py:class:`uplink.Part`.

    Example:
        .. code-block:: python

            @multipart
            @put(/user/photo")
            def update_user(self, photo: Part, description: Part):
                \"""Upload a user profile photo.\"""
    """

    @property
    def converter_key(self):
        """Converts part to the request body."""
        return keys.CONVERT_TO_REQUEST_BODY

    def _modify_request(self, request_builder, value):
        """Updates the request body with the form part."""
        request_builder.info["files"][self.name] = value


class PartMap(TypedArgument):
    """
    A mapping of form field parts.

    Use together with the decorator :py:class:`uplink.multipart` and
    annotate each part of form parts with :py:class:`uplink.PartMap`

    Example:
        .. code-block:: python

            @multipart
            @put(/user/photo")
            def update_user(self, photo: Part, description: Part):
                \"""Upload a user profile photo.\"""
    """

    @property
    def converter_key(self):
        """Converts each part to the request body."""
        return keys.Map(keys.CONVERT_TO_REQUEST_BODY)

    def _modify_request(self, request_builder, value):
        """Updaytes request body to with the form parts."""
        request_builder.info["files"].update(value)


class Body(TypedArgument):
    """
    Set the request body at runtime.

    Use together with the decorator :py:class:`uplink.json`. The method
    argument value will become the request's body when annotated
    with :py:class:`uplink.Body`.

    Example:
        .. code-block:: python

            @json
            @patch(/user")
            def update_user(self, **info: Body):
                \"""Update the current user.\"""
    """
    @property
    def converter_key(self):
        """Converts request body."""
        return keys.CONVERT_TO_REQUEST_BODY

    def _modify_request(self, request_builder, value):
        """Updates request body data."""
        request_builder.info["data"] = value


class Url(ArgumentAnnotation):
    """
    Sets a dynamic URL.

    Provides the URL at runtime as a method argument. Drop the decorator
    parameter path from :py:class:`uplink.get` and annotate the
    corresponding argument with :py:class:`uplink.Url`

    Example:
        .. code-block:: python

            @get
            def get(self, endpoint: Url):
                \"""Execute a GET requests against the given endpoint\"""
    """

    class DynamicUrlAssignmentFailed(exceptions.InvalidRequestDefinition):
        """Raised when the attempt to set dynamic url fails."""
        message = "Failed to set dynamic url annotation on `%s`. "

        def __init__(self, request_definition_builder):
            self.message = self.message % request_definition_builder.__name__

    @property
    def converter_key(self):
        """Converts url type to string."""
        return keys.CONVERT_TO_STRING

    def modify_request_definition(self, request_definition_builder):
        """Sets dynamic url."""
        try:
            request_definition_builder.uri.is_dynamic = True
        except ValueError:
            # TODO: re-raise with ValueError
            raise self.DynamicUrlAssignmentFailed(request_definition_builder)

    @classmethod
    def _modify_request(cls, request_builder, value):
        """Updates request url."""
        request_builder.url = value
