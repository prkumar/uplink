# Third-party imports
import pytest

# Local imports
from uplink import auth, builder, converters, exceptions, helpers
from uplink.clients import io


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
        request_builder.relative_url = "/example/path"
        request_builder.return_type = None
        request_builder.transaction_hooks = ()
        request_builder.request_template = "request_template"
        uplink_builder = mocker.Mock(spec=builder.Builder)
        uplink_builder.converters = ()
        uplink_builder.hooks = ()
        request_preparer = builder.RequestPreparer(uplink_builder)
        execution_builder = mocker.Mock(spec=io.RequestExecutionBuilder)
        request_preparer.prepare_request(request_builder, execution_builder)

        # Verify
        execution_builder.with_client.assert_called_with(uplink_builder.client)
        execution_builder.with_io.assert_called_with(uplink_builder.client.io())
        execution_builder.with_template(request_builder.request_template)

    def test_prepare_request_with_transaction_hook(
        self, mocker, uplink_builder, request_builder, transaction_hook_mock
    ):
        request_builder.method = "METHOD"
        request_builder.relative_url = "/example/path"
        request_builder.request_template = "request_template"
        uplink_builder.base_url = "https://example.com"
        request_builder.transaction_hooks = [transaction_hook_mock]
        request_preparer = builder.RequestPreparer(uplink_builder)
        execution_builder = mocker.Mock(spec=io.RequestExecutionBuilder)
        request_preparer.prepare_request(request_builder, execution_builder)

        # Verify
        transaction_hook_mock.audit_request.assert_called_with(
            None, request_builder
        )
        execution_builder.with_client.assert_called_with(uplink_builder.client)
        execution_builder.with_io.assert_called_with(uplink_builder.client.io())
        execution_builder.with_template(request_builder.request_template)

    def test_create_request_builder(self, mocker, request_definition):
        uplink_builder = mocker.Mock(spec=builder.Builder)
        uplink_builder.converters = ()
        uplink_builder.hooks = ()
        request_definition.make_converter_registry.return_value = {}
        request_preparer = builder.RequestPreparer(uplink_builder)
        request = request_preparer.create_request_builder(request_definition)
        assert isinstance(request, helpers.RequestBuilder)

    def test_create_request_builder_with_session_hooks(
        self, mocker, request_definition, transaction_hook_mock
    ):
        uplink_builder = mocker.Mock(spec=builder.Builder)
        uplink_builder.converters = ()
        uplink_builder.hooks = (transaction_hook_mock,)
        request_definition.make_converter_registry.return_value = {}
        request_preparer = builder.RequestPreparer(uplink_builder)
        request = request_preparer.create_request_builder(request_definition)
        assert transaction_hook_mock.audit_request.called
        assert isinstance(request, helpers.RequestBuilder)


class TestCallFactory(object):
    def test_call(self, mocker, request_definition, request_builder):
        args = ()
        kwargs = {}
        request_preparer = mocker.Mock(spec=builder.RequestPreparer)
        request_preparer.create_request_builder.return_value = request_builder
        execution_builder = mocker.Mock(spec=io.RequestExecutionBuilder)
        execution_builder.build().start.return_value = object()
        factory = builder.CallFactory(
            request_preparer, request_definition, lambda: execution_builder
        )
        assert (
            factory(*args, **kwargs)
            is execution_builder.build().start.return_value
        )
        request_definition.define_request.assert_called_with(
            request_builder, args, kwargs
        )
        request_preparer.prepare_request.assert_called_with(
            request_builder, execution_builder
        )
        execution_builder.build().start.assert_called_with(
            (request_builder.method, request_builder.url, request_builder.info)
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
    assert Consumer.request_method is request_definition_builder.copy()

    # Verify: Try again after resetting
    Consumer.request_method = request_definition_builder
    assert Consumer.request_method is request_definition_builder.copy()

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
