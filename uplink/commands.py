# Standard library imports
import collections
import functools

# Local imports
from uplink import (
    arguments,
    converters,
    decorators,
    exceptions,
    interfaces,
    returns,
    utils,
)

__all__ = ["get", "head", "put", "post", "patch", "delete"]


class MissingArgumentAnnotations(exceptions.InvalidRequestDefinition):
    message = "Missing annotation for argument(s): '%s'."
    implicit_message = " (Implicit path variables: '%s')"

    def __init__(self, missing, path_variables):
        missing, path_variables = list(missing), list(path_variables)
        self.message = self.message % "', '".join(missing)
        if path_variables:  # pragma: no cover
            self.message += self.implicit_message % "', '".join(path_variables)


class MissingUriVariables(exceptions.InvalidRequestDefinition):
    message = "On uri template %s, some variables are not handled: %s"

    def __init__(self, uri, remaining_variables):
        self.message = self.message % (uri, "', '".join(remaining_variables))


class HttpMethodFactory(object):
    def __init__(self, method):
        self._method = method

    def __call__(self, uri=None, args=()):
        if callable(uri) and not args:
            return HttpMethod(self._method)(uri)
        else:
            return HttpMethod(self._method, uri, args)


class HttpMethod(object):
    @staticmethod
    def _add_args(obj):
        return obj

    def __init__(self, method, uri=None, args=None):
        self._method = method
        self._uri = uri

        # Register argument annotations
        if args:
            is_map = isinstance(args, collections.Mapping)
            args, kwargs = ((), args) if is_map else (args, {})
            self._add_args = decorators.args(*args, **kwargs)

    def __call__(self, func):
        spec = utils.get_arg_spec(func)
        arg_handler = arguments.ArgumentAnnotationHandlerBuilder(
            func, spec.args
        )
        builder = RequestDefinitionBuilder(
            self._method,
            URIDefinitionBuilder(self._uri),
            arg_handler,
            decorators.MethodAnnotationHandlerBuilder(),
        )

        # Need to add the annotations after constructing the request
        # definition builder so it has a chance to attach its listener.
        arg_handler.set_annotations(spec.annotations)

        # Use return value type hint as expected return type
        if spec.return_annotation is not None:
            builder = returns.schema(spec.return_annotation)(builder)
        functools.update_wrapper(builder, func)
        builder = self._add_args(builder)
        return builder


class URIDefinitionBuilder(interfaces.UriDefinitionBuilder):
    def __init__(self, uri):
        self._uri = uri
        self._is_dynamic = False
        self._uri_variables = set()

    @property
    def is_static(self):
        return self._uri is not None

    @property
    def is_dynamic(self):
        return self._is_dynamic

    @is_dynamic.setter
    def is_dynamic(self, is_dynamic):
        if self.is_static:
            raise ValueError(
                "Failed to set dynamic URI as URI is already defined: %s"
                % self._uri
            )
        self._is_dynamic = is_dynamic

    def add_variable(self, name):
        if self.is_static and name not in self.remaining_variables:
            raise ValueError(
                "`%s` is not a variable on the uri %s" % (name, self._uri)
            )
        self._uri_variables.add(name)

    @property
    def remaining_variables(self):
        return utils.URIBuilder.variables(self._uri) - self._uri_variables

    def build(self):
        if self.remaining_variables:
            raise MissingUriVariables(self._uri, self.remaining_variables)
        return self._uri


class RequestDefinitionBuilder(interfaces.RequestDefinitionBuilder):
    def __init__(
        self, method, uri, argument_handler_builder, method_handler_builder
    ):
        self._method = method
        self._uri = uri
        self._argument_handler_builder = argument_handler_builder
        self._method_handler_builder = method_handler_builder

        self._argument_handler_builder.listener = self._notify
        self._method_handler_builder.listener = self._notify

    def _notify(self, annotation):
        annotation.modify_request_definition(self)

    @property
    def method(self):
        return self._method

    @property
    def uri(self):
        return self._uri

    @property
    def argument_handler_builder(self):
        return self._argument_handler_builder

    @property
    def method_handler_builder(self):
        return self._method_handler_builder

    def _auto_fill_remaining_arguments(self):
        uri_vars = set(self.uri.remaining_variables)
        missing = list(self.argument_handler_builder.missing_arguments)
        still_missing = set(missing) - uri_vars

        # Preserve order of function parameters.
        matching = [p for p in missing if p in uri_vars]

        if still_missing:
            raise MissingArgumentAnnotations(still_missing, matching)

        path_vars = dict.fromkeys(matching, arguments.Path)
        self.argument_handler_builder.set_annotations(path_vars)

    def build(self):
        if not self._argument_handler_builder.is_done():
            self._auto_fill_remaining_arguments()
        argument_handler = self._argument_handler_builder.build()
        method_handler = self._method_handler_builder.build()
        uri = self._uri.build()
        return RequestDefinition(
            self._method, uri, argument_handler, method_handler
        )


class RequestDefinition(interfaces.RequestDefinition):
    def __init__(self, method, uri, argument_handler, method_handler):
        self._method = method
        self._uri = uri
        self._argument_handler = argument_handler
        self._method_handler = method_handler

    @property
    def argument_annotations(self):
        return tuple(self._argument_handler.annotations)

    @property
    def method_annotations(self):
        return tuple(self._method_handler.annotations)

    def make_converter_registry(self, converters_):
        return converters.ConverterFactoryRegistry(converters_, self)

    def define_request(self, request_builder, func_args, func_kwargs):
        request_builder.method = self._method
        request_builder.url = utils.URIBuilder(self._uri)
        self._argument_handler.handle_call(
            request_builder, func_args, func_kwargs
        )
        self._method_handler.handle_builder(request_builder)
        request_builder.url = request_builder.url.build()


get = HttpMethodFactory("GET").__call__
head = HttpMethodFactory("HEAD").__call__
put = HttpMethodFactory("PUT").__call__
post = HttpMethodFactory("POST").__call__
patch = HttpMethodFactory("PATCH").__call__
delete = HttpMethodFactory("DELETE").__call__
