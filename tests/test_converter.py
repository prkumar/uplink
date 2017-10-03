# Third party import
import requests

# Local imports
from uplink import converter


class TestCast(object):
    def test_converter_without_caster(self, converter_mock):
        converter_mock.convert.return_value = 2
        cast = converter.Cast(None, converter_mock)
        return_value = cast.convert(1)
        converter_mock.convert.assert_called_with(1)
        assert return_value == 2

    def test_convert_with_caster(self, mocker, converter_mock):
        caster = mocker.Mock(return_value=2)
        converter_mock.convert.return_value = 3
        cast = converter.Cast(caster, converter_mock)
        return_value = cast.convert(1)
        caster.assert_called_with(1)
        converter_mock.convert.assert_called_with(2)
        assert return_value == 3


class TestResponseBodyConverter(object):
    def test_convert(self):
        converter_ = converter.ResponseBodyConverter()
        response = "json response"
        converted = converter_.convert(response)
        assert converted == response


class TestRequestBodyConverter(object):
    def test_convert_str(self):
        converter_ = converter.RequestBodyConverter()
        assert converter_.convert("example") == "example"

    def test_convert_obj(self):
        converter_ = converter.RequestBodyConverter()
        example = {"hello": "2"}
        assert converter_.convert(example) == example


class TestStringConverter(object):
    def test_convert(self):
        converter_ = converter.StringConverter()
        assert converter_.convert(2) == "2"


class TestMappingConverterDecorator(object):
    def test_convert(self, mocker, converter_mock):
        mapping = {"key1": "value1", "key2": "value2"}
        converter_mock.convert.return_value = "converted"
        mapping_converter = converter.MappingConverterDecorator(converter_mock)
        converted_value = mapping_converter.convert(mapping)
        calls = map(mocker.call, mapping.values())
        assert converter_mock.convert.mock_calls == list(calls)
        assert converted_value == {"key1": "converted", "key2": "converted"}


class TestConverterFactoryRegistry(object):
    backend = converter.ConverterFactoryRegistry._converter_factory_registry

    def test_init_args_are_passed_to_factory(self, converter_factory_mock):
        args = ("arg1", "arg2")
        kwargs = {"arg3": "arg3"}
        converter_factory_mock.make_string_converter.return_value = "test"
        registry = converter.ConverterFactoryRegistry(
            (converter_factory_mock,), *args, **kwargs)
        return_value = registry[converter.CONVERT_TO_STRING]()
        converter_factory_mock.make_string_converter.assert_called_with(
            *args, **kwargs
        )
        assert return_value == "test"

    def test_with_converter_map(self, converter_factory_mock):
        registry = converter.ConverterFactoryRegistry((converter_factory_mock,))
        converter_ = registry[converter.Map(converter.CONVERT_TO_STRING)]()
        assert isinstance(converter_, converter.MappingConverterDecorator)

    def test_len(self):
        registry = converter.ConverterFactoryRegistry(())
        assert len(registry) == len(self.backend)

    def test_iter(self):
        registry = converter.ConverterFactoryRegistry(())
        assert list(iter(registry)) == list(iter(self.backend))


def test_make_request_body_converter(converter_factory_mock):
    method = converter.make_request_body_converter(converter_factory_mock)
    assert method is converter_factory_mock.make_request_body_converter


def test_make_response_body_converter(converter_factory_mock):
    method = converter.make_response_body_converter(converter_factory_mock)
    assert method is converter_factory_mock.make_response_body_converter


def test_make_string_converter(converter_factory_mock):
    method = converter.make_string_converter(converter_factory_mock)
    assert method is converter_factory_mock.make_string_converter
