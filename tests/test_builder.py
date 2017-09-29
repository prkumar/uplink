# Third party imports
import pytest

# Local imports
from uplink import builder, converter, client, exceptions, utils


@pytest.fixture
def fake_service_cls(request_definition_builder, request_definition):
    class Service(object):
        builder = request_definition_builder
    request_definition_builder.build.return_value = request_definition
    return Service


@pytest.fixture
def uplink_builder():
    return builder.Builder(None)


class TestResponseConverter(object):
    def test_handle_response(self, mocker, http_client_mock):
        converter_ = mocker.Mock()
        input_value = "converted"
        converter_.return_value = input_value
        rc = builder.ResponseConverter(http_client_mock, converter_)
        assert rc.handle_response(None) is input_value


class TestRequestPreparer(object):
    def test_prepare_request(
            self,
            http_client_mock,
            request_definition,
            uplink_builder
    ):
        request = utils.Request("METHOD", "/example/path", {}, None)
        uplink_builder.client = http_client_mock
        uplink_builder.base_url = "https://example.com"
        request_preparer = builder.RequestPreparer(
            uplink_builder, request_definition
        )
        return_value = request_preparer.prepare_request(request)
        assert return_value[0] == "METHOD"
        assert return_value[1] == "https://example.com/example/path"
        assert return_value[2] == {}


class TestCallFactory(object):
    def test_call(self, mocker, request_definition, request_builder):
        instance = object()
        args = ()
        kwargs = {}
        request_preparer = mocker.Mock(spec=builder.RequestPreparer)
        request_preparer.create_request_builder.return_value = request_builder
        factory = builder.CallFactory(
            instance,
            request_preparer,
            request_definition)
        assert isinstance(factory(*args, **kwargs), builder.Call)
        request_definition.define_request.assert_called_with(
            request_builder, (instance,) + args, kwargs
        )
        assert request_builder.build.called


class TestCall(object):
    def test_return_type(self):
        call = builder.Call(None, str)
        assert call.return_type is str

    def test_execute(self, mocker):
        prepared_request = mocker.Mock(spec=client.PreparedRequest)
        call = builder.Call(prepared_request, None)
        call.execute()
        prepared_request.send.assert_called_with()


class TestBuilder(object):
    def test_init_adds_standard_converter_factory(self, uplink_builder):
        assert isinstance(
            uplink_builder._converter_factories[0],
            converter.StandardConverterFactory
        )

    def test_client_getter(self, uplink_builder):
        assert isinstance(uplink_builder.client, client.BaseHttpClient)

    def test_client_setter(self, uplink_builder, http_client_mock):
        uplink_builder.client = http_client_mock
        assert uplink_builder._client is http_client_mock

    def test_base_url(self, uplink_builder):
        uplink_builder.base_url = "example"
        assert uplink_builder._base_url == "example"

    def test_add_converter_factory(self,
                                   uplink_builder,
                                   converter_factory_mock):
        uplink_builder.add_converter_factory(converter_factory_mock)
        factory = list(uplink_builder.converter_factories)[0]
        assert factory == converter_factory_mock

    def test_build(self, fake_service_cls):
        service = builder.Builder(fake_service_cls).build()
        assert isinstance(service, fake_service_cls)

    def test_build_failure(self, fake_service_cls):
        exception = exceptions.InvalidRequestDefinition()
        fake_service_cls.builder.build.side_effect = exception
        uplink = builder.Builder(fake_service_cls)
        with pytest.raises(exceptions.UplinkBuilderError):
            uplink.build()


def test_build(mocker, http_client_mock):
    builder_cls_mock = mocker.Mock()
    builder_mock = mocker.Mock(spec=builder.Builder)
    builder_cls_mock.return_value = builder_mock
    mocker.patch.object(builder, "Builder", builder_cls_mock)
    builder.build(
        fake_service_cls,
        base_url="example.com",
        http_client=http_client_mock
    )
    assert builder_mock.base_url == "example.com"
    builder_mock.add_converter_factory.assert_called_with()
    assert builder_mock.client is http_client_mock
