# Standard library imports
import collections
import warnings

# Local imports
from uplink import (
    hooks,
    clients,
    converters,
    interfaces,
    exceptions,
    helpers,
    utils
)

__all__ = ["build", "Consumer"]


class ResponseConverter(hooks.TransactionHookDecorator):
    # TODO: Override `audit_request` to log request details

    def __init__(self, connection, convert):
        super(ResponseConverter, self).__init__(connection)
        self._convert = convert

    def handle_response(self, response):
        response = super(ResponseConverter, self).handle_response(response)
        return self._convert(response)


class RequestHandler(object):

    def __init__(self, hook, method, url, extras):
        self._args = (method, url, extras)
        self._hook = hook

    def fulfill(self, request):
        self._hook.audit_request(*self._args)
        request.add_callback(self._hook.handle_response)
        return request.send(*self._args)


class RequestPreparer(object):

    def __init__(self, uplink_builder, definition):
        self._hook = uplink_builder.hook
        self._client = clients.get_client(uplink_builder.client)
        self._base_url = str(uplink_builder.base_url)
        self._converter_registry = self._make_converter_registry(
            uplink_builder, definition
        )

    @staticmethod
    def _make_converter_registry(uplink_builder, request_definition):
        return converters.ConverterFactoryRegistry(
            uplink_builder.converters,
            argument_annotations=request_definition.argument_annotations,
            request_annotations=request_definition.method_annotations
        )

    def _join_uri_with_base(self, url):
        return utils.urlparse.urljoin(self._base_url, url)

    def _get_converter(self, request):
        f = self._converter_registry[converters.keys.CONVERT_FROM_RESPONSE_BODY]
        return f(request.return_type).convert

    def prepare_request(self, request):
        url = self._join_uri_with_base(request.uri)
        convert = self._get_converter(request)
        hook = ResponseConverter(self._hook, convert)
        request_handler = RequestHandler(
            hook, request.method, url, request.info)
        return request_handler.fulfill(self._client.create_request())

    def create_request_builder(self):
        return helpers.RequestBuilder(self._converter_registry)


class CallFactory(object):
    def __init__(self, request_preparer, request_definition):
        self._request_preparer = request_preparer
        self._request_definition = request_definition

    def __call__(self, *args, **kwargs):
        builder = self._request_preparer.create_request_builder()
        self._request_definition.define_request(builder, args, kwargs)
        request = builder.build()
        return self._request_preparer.prepare_request(request)


class Builder(interfaces.CallBuilder):
    """The default callable builder."""

    def __init__(self):
        self._base_url = ""
        self._hook = hooks.TransactionHook()
        self._client = clients.DEFAULT_CLIENT
        self._converters = collections.deque()
        self._converters.append(converters.StandardConverter())

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, client):
        self._client = client

    @property
    def hook(self):
        return self._hook

    @hook.setter
    def hook(self, hook):
        self._hook = hook

    @property
    def base_url(self):
        return self._base_url

    @base_url.setter
    def base_url(self, base_url):
        self._base_url = base_url

    @property
    def converters(self):
        return iter(self._converters)

    def add_converter(self, *converters_):
        self._converters.extendleft(converters_)

    @utils.memoize()
    def build(self, definition):
        """
        Creates a callable that uses the provided definition to execute
        HTTP requests when invoked.
        """
        return CallFactory(RequestPreparer(self, definition), definition)


class ConsumerMethod(object):
    """
    A wrapper around a :py:class`interfaces.RequestDefinitionBuilder`
    instance bound to a :py:class:`Consumer` subclass, mainly responsible
    for controlling access to the instance.
    """

    def __init__(self, owner_name, attr_name, request_definition_builder):
        self._request_definition_builder = request_definition_builder
        self._owner_name = owner_name
        self._attr_name = attr_name
        self._request_definition = self._build_definition()

    def _build_definition(self):
        try:
            return self._request_definition_builder.build()
        except exceptions.InvalidRequestDefinition as error:
            # TODO: Find a Python 2.7 compatible way to reraise
            raise exceptions.UplinkBuilderError(
                self._owner_name,
                self._attr_name,
                error)

    def __get__(self, instance, owner):
        if instance is None:
            return self._request_definition_builder
        else:
            return instance._builder.build(self._request_definition)


class ConsumerMeta(type):
    @staticmethod
    def _wrap_if_definition(cls_name, key, value):
        if isinstance(value, interfaces.RequestDefinitionBuilder):
            value = ConsumerMethod(cls_name, key, value)
        return value

    def __new__(mcs, name, bases, namespace):
        # Wrap all definition builders with a special descriptor that
        # handles attribute access behavior.
        for key, value in namespace.items():
            namespace[key] = mcs._wrap_if_definition(name, key, value)
        return super(ConsumerMeta, mcs).__new__(mcs, name, bases, namespace)

    def __setattr__(cls, key, value):
        value = cls._wrap_if_definition(cls.__name__, key, value)
        super(ConsumerMeta, cls).__setattr__(key, value)


_Consumer = ConsumerMeta("_Consumer", (), {})


class Consumer(_Consumer):

    def __init__(
            self,
            base_url="",
            client=None,
            hook=None,
            converter=()
    ):
        self._builder = Builder()
        self._builder.base_url = base_url
        if isinstance(converter, converters.interfaces.ConverterFactory):
            converter = (converter,)
        self._builder.add_converter(*converter)
        if client is not None:
            self._builder.client = client
        if hook is not None:
            self._builder.hook = hook


def build(service_cls, *args, **kwargs):
    name = service_cls.__name__
    warnings.warn(
        "`uplink.build` is deprecated and will be removed in v1.0.0. "
        "To construct a consumer instance, have `{0}` inherit "
        "`uplink.Consumer` then instantiate (e.g., `{0}(...)`). ".format(name),
        DeprecationWarning
    )
    consumer = type(name, (service_cls, Consumer), dict(service_cls.__dict__))
    return consumer(*args, **kwargs)
