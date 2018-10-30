# Third party imports
import pytest

# Local imports
from uplink import auth, builder, converters, exceptions, helpers


@pytest.fixture
def fake_service_cls(request_definition_builder, request_definition):
    class Service(object):
        builder = request_definition_builder

    request_definition_builder.build.return_value = request_definition
    return Service


@pytest.fixture
def uplink_builder(http_client_mock):
    b = builder.Builder()
    b.client = http_client_mock
    return b


class TestRequestPreparer(object):
    def test_prepare_request(self, mocker, request_builder):
        request_builder.method = "METHOD"
        request_builder.url = "/example/path"
        request_builder.return_type = None
        request_builder.transaction_hooks = ()
        uplink_builder = mocker.Mock(spec=builder.Builder)
        uplink_builder.converters = ()
        uplink_builder.hooks = ()
        request_preparer = builder.RequestPreparer(uplink_builder)
        request_preparer.prepare_request(request_builder)
        uplink_builder.client.create_request().send.assert_called_with(
            request_builder.method, request_builder.url, request_builder.info
        )

    def test_prepare_request_with_transaction_hook(
        self, uplink_builder, request_builder, transaction_hook_mock
    ):
        request_builder.method = "METHOD"
        request_builder.url = "/example/path"
        uplink_builder.base_url = "https://example.com"
        uplink_builder.add_hook(transaction_hook_mock)
        request_preparer = builder.RequestPreparer(uplink_builder)
        request_preparer.prepare_request(request_builder)
        transaction_hook_mock.audit_request.assert_called_with(
            None, request_builder
        )
        uplink_builder.client.create_request().send.assert_called_with(
            request_builder.method, request_builder.url, request_builder.info
        )

    def test_create_request_builder(self, uplink_builder, request_definition):
        request_definition.make_converter_registry.return_value = {}
        request_preparer = builder.RequestPreparer(uplink_builder)
        request = request_preparer.create_request_builder(request_definition)
        assert isinstance(request, helpers.RequestBuilder)


class TestCallFactory(object):
    def test_call(self, mocker, request_definition, request_builder):
        args = ()
        kwargs = {}
        request_preparer = mocker.Mock(spec=builder.RequestPreparer)
        request_preparer.create_request_builder.return_value = request_builder
        factory = builder.CallFactory(request_preparer, request_definition)
        assert (
            factory(*args, **kwargs)
            is request_preparer.prepare_request.return_value
        )
        request_definition.define_request.assert_called_with(
            request_builder, args, kwargs
        )


class TestBuilder(object):
    def test_init_adds_standard_converter_factory(self, uplink_builder):
        assert isinstance(
            uplink_builder.converters[-1], converters.StandardConverter
        )

    def test_client_getter(self, uplink_builder, http_client_mock):
        uplink_builder.client = http_client_mock
        assert uplink_builder.client is http_client_mock

    def test_client_setter(self, uplink_builder, http_client_mock):
        uplink_builder.client = http_client_mock
        assert uplink_builder._client is http_client_mock

    def test_base_url(self, uplink_builder):
        uplink_builder.base_url = "example"
        assert uplink_builder._base_url == "example"

    def test_add_converter_factory(
        self, uplink_builder, converter_factory_mock
    ):
        uplink_builder.converters = (converter_factory_mock,)
        factory = list(uplink_builder.converters)[0]
        assert factory == converter_factory_mock

    def test_build(self, request_definition, uplink_builder):
        call = uplink_builder.build(request_definition)
        assert isinstance(call, builder.CallFactory)


def test_build_failure(fake_service_cls):
    exception = exceptions.InvalidRequestDefinition()
    fake_service_cls.builder.build.side_effect = exception
    fake_service_cls.builder.__name__ = "builder"
    with pytest.raises(exceptions.UplinkBuilderError):
        builder.build(fake_service_cls, base_url="example.com")


def test_build(
    mocker,
    http_client_mock,
    converter_factory_mock,
    fake_service_cls,
    transaction_hook_mock,
):
    # Monkey-patch the Builder class.
    builder_cls_mock = mocker.Mock()
    builder_mock = builder.Builder()
    builder_cls_mock.return_value = builder_mock
    mocker.patch.object(builder, "Builder", builder_cls_mock)

    builder.build(
        fake_service_cls,
        base_url="example.com",
        client=http_client_mock,
        converter=converter_factory_mock,
        auth=("username", "password"),
        hook=transaction_hook_mock,
    )
    assert builder_mock.base_url == "example.com"
    assert builder_mock.client is http_client_mock
    assert list(builder_mock.converters)[0] is converter_factory_mock
    assert isinstance(builder_mock.auth, auth.BasicAuth)


def test_setting_request_method(request_definition_builder):
    # We need this test, since we wrap the request definition builders and
    # want to ensure that we unwrap on attribute access.

    class Consumer(builder.Consumer):
        request_method = request_definition_builder

    # Verify: Get request definition builder on access
    assert Consumer.request_method is request_definition_builder

    # Verify: Try again after resetting
    Consumer.request_method = request_definition_builder
    assert Consumer.request_method is request_definition_builder

    # Verify: We get callable on attribute access for an instance
    consumer = Consumer()
    assert callable(consumer.request_method)


def test_inject(mocker, fake_service_cls, transaction_hook_mock):
    # Monkey-patch the Builder class.
    builder_cls_mock = mocker.Mock()
    builder_mock = mocker.Mock(wraps=builder.Builder())
    builder_cls_mock.return_value = builder_mock
    mocker.patch.object(builder, "Builder", builder_cls_mock)

    service = builder.build(fake_service_cls)

    # Verify
    service._inject(transaction_hook_mock)
    builder_mock.add_hook.assert_called_with(transaction_hook_mock)
