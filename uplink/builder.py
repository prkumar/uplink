# Standard library imports
import collections

# Local imports
from uplink import client, converter, interfaces, exceptions, helpers, utils

__all__ = ["Builder", "build", "Consumer"]


class ResponseConverter(client.HttpClientDecorator):
    # TODO: Override `audit_request` to log request details

    def __init__(self, connection, convert):
        super(ResponseConverter, self).__init__(connection)
        self._convert = convert

    def handle_response(self, response):
        response = super(ResponseConverter, self).handle_response(response)
        return self._convert(response)


class RequestPreparer(object):

    def __init__(self, uplink_builder, definition):
        self._client = uplink_builder.client
        self._base_url = uplink_builder.base_url
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
        client_ = ResponseConverter(self._client, convert)
        return client_.build_request(request.method, url, request.info)

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

    def __init__(self, service_stub):
        """
        Creates a Builder.

        Args:
            service_stub: An initiated instance of the class being built, with
                no functions or fields.
        """

        self._base_url = ""
        self._service_stub = service_stub
        self._client = client.HttpClient()
        self._converter_factories = collections.deque()
        self._converter_factories.append(converter.StandardConverterFactory())

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, new_client):
        assert isinstance(new_client, client.BaseHttpClient)
        self._client = new_client

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

    def _make_call_factory(self, service, definition):
        return CallFactory(
            service,
            RequestPreparer(self, definition),
            definition,
        )

    @staticmethod
    def _bind_to_instance(instance, attribute_name, call_factory):
        setattr(instance, attribute_name, call_factory)

    def build(self):
        """
        Modifies the internal service stub by binding functions to it,
        and returns the modified stub
        """

        definition_builders = helpers.get_api_definitions(self._service_stub.__class__)

        # Build and bind API definitions to service instance.
        for attribute_name, builder in definition_builders:
            try:
                definition = builder.build(self)
            except exceptions.InvalidRequestDefinition as error:
                # TODO: Find a Python 2.7 compatible way to reraise
                raise exceptions.UplinkBuilderError(
                    self._service_stub.__class__, attribute_name, error)
            call_factory = self._make_call_factory(self._service_stub, definition)
            self._bind_to_instance(self._service_stub, attribute_name, call_factory)
        return self._service_stub


class Consumer(object):

    def __init__(self, base_url="", converter_factories=(), http_client=None):
        builder = Builder(self)
        builder.base_url = base_url
        builder.add_converter_factory(*converter_factories)
        if http_client is not None:
            builder.client = http_client
        builder.build()


def build(service_cls, base_url="", converter_factories=(), http_client=None):
    builder = Builder(service_cls())
    builder.base_url = base_url
    builder.add_converter_factory(*converter_factories)
    if http_client is not None:
        builder.client = http_client
    return builder.build()
