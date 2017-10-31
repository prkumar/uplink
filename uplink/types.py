"""
This module implements the built-in argument annotations and their
handling classes.
"""


# Standard library imports
import collections
import inspect

# Local imports
from uplink import converter, exceptions, interfaces, utils

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


class MissingArgumentAnnotations(exceptions.InvalidRequestDefinition):
    message = "Missing annotation for argument(s): '%s'."
    implicit_message = " (Implicit path variables: '%s')"

    def __init__(self, missing, path_variables):
        missing, path_variables = list(missing), list(path_variables)
        self.message = self.message % "', '".join(missing)
        if path_variables:
            self.message += self.implicit_message % "', '".join(path_variables)


class ArgumentAnnotationHandlerBuilder(
    interfaces.AnnotationHandlerBuilder
):
    def __init__(self, func, arguments, func_is_method=True):
        self._arguments = arguments[func_is_method:]
        self._argument_types = collections.OrderedDict.fromkeys(self._arguments)
        self._defined = 0
        self._func = func

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

    def _auto_fill_remaining_arguments(self):
        uri_vars = set(self.request_definition_builder.uri.remaining_variables)
        missing = list(self.missing_arguments)
        still_missing = set(missing) - uri_vars

        # Preserve order of function parameters.
        matching = [p for p in missing if p in uri_vars]

        if still_missing:
            raise MissingArgumentAnnotations(still_missing, matching)
        self.set_annotations(dict.fromkeys(matching, Path))

    def build(self):
        if not self.is_done():
            self._auto_fill_remaining_arguments()
        return ArgumentAnnotationHandler(
            self._func,
            self._argument_types,
        )


class ArgumentAnnotationHandler(interfaces.AnnotationHandler):

    def __init__(self, func, arguments):
        self._func = func
        self._arguments = arguments

    @property
    def annotations(self):
        return iter(self._arguments.values())

    def get_relevant_arguments(self, call_args):
        return filter(call_args.__contains__, self._arguments)

    def handle_call(self, request_builder, func_args, func_kwargs):
        call_args = utils.get_call_args(self._func, *func_args, **func_kwargs)
        for name in self.get_relevant_arguments(call_args):
            self.handle_argument(
                request_builder,
                self._arguments[name],
                call_args[name]
            )

    @staticmethod
    def handle_argument(request_builder, argument, value):
        argument_type, converter_key = argument.type, argument.converter_type
        converter_ = request_builder.get_converter(converter_key, argument_type)
        value = converter_.convert(value)

        # TODO: Catch Annotation errors and chain them here + provide context.
        argument.modify_request(request_builder, value)


class ArgumentAnnotation(interfaces.Annotation):
    can_be_static = True

    def __call__(self, request_definition_builder):
        request_definition_builder.argument_handler_builder.add_annotation(self)
        return request_definition_builder

    def modify_request_definition(self, request_definition_builder):
        pass

    def modify_request(self, request_builder, value):
        raise NotImplementedError

    @property
    def type(self):
        return None

    @property
    def converter_type(self):
        raise NotImplementedError


class TypedArgument(ArgumentAnnotation):

    def __init__(self, type=None):
        self._type = type

    @property
    def type(self):
        return self._type

    @property
    def converter_type(self):
        raise NotImplementedError

    def modify_request(self, request_builder, value):
        raise NotImplementedError


class NamedArgument(TypedArgument):
    can_be_static = True

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
    def converter_type(self):
        raise NotImplementedError

    def modify_request(self, request_builder, value):
        raise NotImplementedError


class Path(NamedArgument):
    """
    Substitution of a path variable in a `URI template
    <https://tools.ietf.org/html/rfc6570>`__.

    URI template parameters are enclosed in braces (e.g.,
    :code:`{name}`). To map an argument to a declared URI parameter, use
    the :py:class:`Path` annotation:

    .. code-block:: python

        class TodoService(object):
            @get("todos{/id}")
            def get_todo(self, todo_id: Path("id")): pass

    Then, invoking :code:`get_todo` with a consumer instance:

    .. code-block:: python

        todo_service.get_todo(100)

    creates an HTTP request with a URL ending in :code:`todos/100`.

    Note:
        When building the consumer instance, :py:func:`uplink.build` will try
        match unannotated function arguments with URL path parameters. See
        :ref:`implicit_path_annotations` for details.

        For example, we could rewrite the method from the previous
        example as:

        .. code-block:: python

            @get("todos{/id}")
            def get_todo(self, id): pass
    """

    @property
    def converter_type(self):
        return converter.CONVERT_TO_STRING

    def modify_request_definition(self, request_definition_builder):
        request_definition_builder.uri.add_variable(self.name)

    def modify_request(self, request_builder, value):
        request_builder.uri.set_variable({self.name: value})


class Query(NamedArgument):

    @staticmethod
    def convert_to_string(value):
        # TODO: Move this responsibility to the `converter`
        # Convert to string or list of strings.
        if isinstance(value, (list, tuple)):
            return list(map(str, value))
        else:
            return str(value)

    @property
    def converter_type(self):
        return converter.CONVERT_TO_REQUEST_BODY

    def modify_request(self, request_builder, value):
        value = self.convert_to_string(value)
        request_builder.info["params"][self.name] = value


class QueryMap(TypedArgument):

    @property
    def converter_type(self):
        return converter.Map(converter.CONVERT_TO_REQUEST_BODY)

    @classmethod
    def modify_request(cls, request_builder, value):
        value = dict((k, Query.convert_to_string(value[k])) for k in value)
        request_builder.info["params"].update(value)


class Header(NamedArgument):

    @property
    def converter_type(self):
        return converter.CONVERT_TO_STRING

    def modify_request(self, request_builder, value):
        request_builder.info["headers"][self.name] = value


class HeaderMap(TypedArgument):

    @property
    def converter_type(self):
        return converter.Map(converter.CONVERT_TO_STRING)

    @classmethod
    def modify_request(cls, request_builder, value):
        request_builder.info["headers"].update(value)


class Field(NamedArgument):

    class FieldAssignmentFailed(exceptions.AnnotationError):
        message = (
            "Failed to define field '%s' to request body. Another argument "
            "annotation might have overwritten the body entirely."
        )

        def __init__(self, field):
            self.message = self.message % field.name

    @property
    def converter_type(self):
        return converter.CONVERT_TO_STRING

    def modify_request(self, request_builder, value):
        try:
            request_builder.info["data"][self.name] = value
        except TypeError:
            # TODO: re-raise with TypeError
            # `data` does not support item assignment
            raise self.FieldAssignmentFailed(self)


class FieldMap(TypedArgument):

    class FieldMapUpdateFailed(exceptions.AnnotationError):
        message = (
            "Failed to update request body with field map. Another argument "
            "annotation might have overwritten the body entirely."
        )

    @property
    def converter_type(self):
        return converter.Map(converter.CONVERT_TO_STRING)

    def modify_request(self, request_builder, value):
        try:
            request_builder.info["data"].update(value)
        except AttributeError:
            # TODO: re-raise with AttributeError
            raise self.FieldMapUpdateFailed()


class Part(NamedArgument):

    @property
    def converter_type(self):
        return converter.CONVERT_TO_REQUEST_BODY

    def modify_request(self, request_builder, value):
        request_builder.info["files"][self.name] = value


class PartMap(TypedArgument):

    @property
    def converter_type(self):
        return converter.Map(converter.CONVERT_TO_REQUEST_BODY)

    def modify_request(self, request_builder, value):
        request_builder.info["files"].update(value)


class Body(TypedArgument):

    @property
    def converter_type(self):
        return converter.CONVERT_TO_REQUEST_BODY

    def modify_request(self, request_builder, value):
        request_builder.info["data"] = value


class Url(ArgumentAnnotation):

    class DynamicUrlAssignmentFailed(exceptions.AnnotationError):
        message = "Failed to set dynamic url annotation on `%s`. "

        def __init__(self, request_definition_builder):
            self.message = self.message % request_definition_builder.__name__

    @property
    def converter_type(self):
        return converter.CONVERT_TO_STRING

    def modify_request_definition(self, request_definition_builder):
        try:
            request_definition_builder.uri.is_dynamic = True
        except ValueError:
            # TODO: re-raise with ValueError
            raise self.DynamicUrlAssignmentFailed(request_definition_builder)

    @classmethod
    def modify_request(cls, request_builder, value):
        request_builder.uri = value
