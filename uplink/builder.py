# Standard library imports
import collections

# Local imports
from uplink import (
    hooks, backend, converter, interfaces, exceptions, helpers, utils
)

__all__ = ["Builder", "build", "Consumer"]


class ResponseConverter(hooks.TransactionHookDecorator):
    # TODO: Override `audit_request` to log request details

    def __init__(self, connection, convert):
        super(ResponseConverter, self).__init__(connection)
        self._convert = convert

    def handle_response(self, response):
        response = super(ResponseConverter, self).handle_response(response)
        return self._convert(response)


class RequestHandler(backend.interfaces.RequestHandler):

    def __init__(self, hook, method, url, extras):
        self._args = (method, url, extras)
        self._hook = hook

    def fulfill(self, request):
        self._hook.audit_request(*self._args)
        request.add_callback(self._hook.handle_response)
        return request.send(*self._args)


class PreparedRequest(object):

    def __init__(self, backend_, request_handler):
        self._backend = backend_
        self._request_handler = request_handler

    def execute(self):
        return self._backend.send_synchronous_request(self._request_handler)

    def enqueue(self):
        return self._backend.send_asynchronous_request(self._request_handler)


class RequestPreparer(object):

    def __init__(self, uplink_builder, definition):
        self._hook = uplink_builder.hook
        self._backend = uplink_builder.client.make_backend()
        self._base_url = str(uplink_builder.base_url)
        self._converter_registry = self._make_converter_registry(
            uplink_builder, definition
        )

    @staticmethod
    def _make_converter_registry(uplink_builder, request_definition):
        return converter.ConverterFactoryRegistry(
            uplink_builder.converter_factories,
            argument_annotations=request_definition.argument_annotations,
            request_annotations=request_definition.method_annotations
        )

    def _join_uri_with_base(self, url):
        return utils.urlparse.urljoin(self._base_url, url)

    def _get_converter(self, request):
        factory = self._converter_registry[converter.CONVERT_FROM_RESPONSE_BODY]
        return factory(request.return_type).convert

    def prepare_request(self, request):
        url = self._join_uri_with_base(request.uri)
        convert = self._get_converter(request)
        hook = ResponseConverter(self._hook, convert)
        request_handler = RequestHandler(
            hook, request.method, url, request.info)
        return PreparedRequest(self._backend, request_handler)

    def create_request_builder(self):
        return helpers.RequestBuilder(self._converter_registry)


class CallFactory(object):
    def __init__(self, instance, request_preparer, request_definition):
        self._instance = instance
        self._request_preparer = request_preparer
        self._request_definition = request_definition

    def __call__(self, *args, **kwargs):
        args = (self._instance,) + args
        builder = self._request_preparer.create_request_builder()
        self._request_definition.define_request(builder, args, kwargs)
        request = builder.build()
        return self._request_preparer.prepare_request(request)


class Builder(interfaces.AbstractUplinkBuilder):

    def __init__(self):
        """
        Creates a Builder.
        """

        self._base_url = ""
        self._hook = hooks.TransactionHook()
        self._client = backend.DEFAULT_BACKEND
        self._converter_factories = collections.deque()
        self._converter_factories.append(converter.StandardConverterFactory())

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, new_client):
        assert isinstance(new_client, backend.interfaces.BackendFactory)
        self._client = new_client

    @property
    def hook(self):
        return self._hook

    @hook.setter
    def hook(self, hook):
        assert isinstance(hook, hooks.BaseTransactionHook)
        self._hook = hook

    @property
    def base_url(self):
        return self._base_url

    @base_url.setter
    def base_url(self, base_url):
        self._base_url = base_url

    @property
    def converter_factories(self):
        return iter(self._converter_factories)

    def add_converter_factory(self, *converter_factories):
        self._converter_factories.extendleft(converter_factories)

    def build(self, consumer, definition):
        """
        Modifies the internal service stub by binding functions to it,
        and returns the modified stub
        """

        try:
            definition = definition.build()
        except exceptions.InvalidRequestDefinition as error:
            # TODO: Find a Python 2.7 compatible way to reraise
            raise exceptions.UplinkBuilderError(
                consumer.__class__, definition.__name__, error)

        return CallFactory(
            consumer,
            RequestPreparer(self, definition),
            definition
        )


class Consumer(object):

    def __init__(
            self,
            base_url="",
            http_client=None,
            hook=None,
            converter_factories=()
    ):
        builder = Builder()
        builder.base_url = base_url
        builder.add_converter_factory(*converter_factories)
        if http_client is not None:
            builder.client = http_client
        if hook is not None:
            builder.hook = hook

        definition_builders = helpers.get_api_definitions(self)
        for attribute_name, definition_builder in definition_builders:
            caller = builder.build(self, definition_builder)
            setattr(self, attribute_name, caller)


def build(service_cls, *args, **kwargs):
    # TODO: DEPRECATE!
    consumer_cls = type(service_cls.__name__, (service_cls, Consumer), {})
    return consumer_cls(*args, **kwargs)
