# Standard library imports
import typing

# Third party imports
import marshmallow
import pytest

# Local imports
from uplink import converters
from uplink.converters import register, standard


class TestCast(object):
    def test_converter_without_caster(self, mocker):
        converter_mock = mocker.stub()
        converter_mock.return_value = 2
        cast = standard.Cast(None, converter_mock)
        return_value = cast.convert(1)
        converter_mock.assert_called_with(1)
        assert return_value == 2

    def test_convert_with_caster(self, mocker):
        caster = mocker.Mock(return_value=2)
        converter_mock = mocker.Mock(return_value=3)
        cast = standard.Cast(caster, converter_mock)
        return_value = cast.convert(1)
        caster.assert_called_with(1)
        converter_mock.assert_called_with(2)
        assert return_value == 3


class TestRequestBodyConverter(object):
    def test_convert_str(self):
        converter_ = standard.RequestBodyConverter()
        assert converter_.convert("example") == "example"

    def test_convert_obj(self):
        converter_ = standard.RequestBodyConverter()
        example = {"hello": "2"}
        assert converter_.convert(example) == example


class TestStringConverter(object):
    def test_convert(self):
        converter_ = standard.StringConverter()
        assert converter_.convert(2) == "2"


class TestStandardConverter(object):
    def test_make_response_body_converter(self):
        # Setup
        converter = standard.StandardConverter()

        # Run & Verify: Pass-through callables
        def f(_): pass
        assert f is converter.make_response_body_converter(f)

        # Run & Verify: Otherwise, return None
        assert None is converter.make_response_body_converter("converter")


class TestConverterFactoryRegistry(object):
    backend = converters.ConverterFactoryRegistry._converter_factory_registry

    def test_init_args_are_passed_to_factory(self, converter_factory_mock, converter_mock):
        args = ("arg1", "arg2")
        kwargs = {"arg3": "arg3"}
        converter_factory_mock.make_string_converter.return_value = converter_mock
        registry = converters.ConverterFactoryRegistry(
            (converter_factory_mock,), *args, **kwargs)
        return_value = registry[converters.keys.CONVERT_TO_STRING]()
        converter_factory_mock.make_string_converter.assert_called_with(
            *args, **kwargs
        )
        assert return_value is converter_mock

    def test_hooks(self, converter_factory_mock, converter_mock):
        converter_factory_mock.make_string_converter.return_value = converter_mock
        registry = converters.ConverterFactoryRegistry((converter_factory_mock,))
        registry[converters.keys.CONVERT_TO_STRING]()
        assert converter_mock.set_chain.called

    def test_len(self):
        registry = converters.ConverterFactoryRegistry(())
        assert len(registry) == len(self.backend)

    def test_iter(self):
        registry = converters.ConverterFactoryRegistry(())
        assert list(iter(registry)) == list(iter(self.backend))


def test_make_request_body_converter(converter_factory_mock):
    method = converters.make_request_body_converter(converter_factory_mock)
    assert method is converter_factory_mock.make_request_body_converter


def test_make_response_body_converter(converter_factory_mock):
    method = converters.make_response_body_converter(converter_factory_mock)
    assert method is converter_factory_mock.make_response_body_converter


def test_make_string_converter(converter_factory_mock):
    method = converters.make_string_converter(converter_factory_mock)
    assert method is converter_factory_mock.make_string_converter


@pytest.fixture(params=["class", "instance"])
def schema_mock_and_argument(request, mocker):
    class Schema(marshmallow.Schema):
        def __new__(cls, *args, **kwargs):
            return schema

    schema = mocker.Mock(spec=marshmallow.Schema)
    if request.param == "class":
        return schema, Schema
    else:
        return schema, schema


class TestMarshmallowConverter(object):
    def test_init_without_marshmallow(self):
        old_marshmallow = converters.MarshmallowConverter.marshmallow
        converters.MarshmallowConverter.marshmallow = None
        with pytest.raises(ImportError):
            converters.MarshmallowConverter()
        converters.MarshmallowConverter.marshmallow = old_marshmallow

    def test_make_request_body_converter(self, mocker, schema_mock_and_argument):
        # Setup
        schema_mock, argument = schema_mock_and_argument
        expected_result = "data"
        dump_result = mocker.Mock()
        dump_result.data = expected_result
        schema_mock.dump.return_value = dump_result
        converter = converters.MarshmallowConverter()
        request_body = {"id": 0}

        # Run
        c = converter.make_request_body_converter(argument)
        result = c.convert(request_body)

        # Verify
        schema_mock.dump.assert_called_with(request_body)
        assert expected_result == result

    def test_make_request_body_converter_without_schema(self):
        # Setup
        converter = converters.MarshmallowConverter()

        # Run
        c = converter.make_request_body_converter("not a schema")

        # Verify
        assert c is None

    def test_make_response_body_converter(self, mocker, schema_mock_and_argument):
        # Setup
        schema_mock, argument = schema_mock_and_argument
        expected_result = "data"
        load_result = mocker.Mock()
        load_result.data = expected_result
        schema_mock.load.return_value = load_result
        converter = converters.MarshmallowConverter()
        response = mocker.Mock()

        # Run
        c = converter.make_response_body_converter(argument)
        result = c.convert(response)

        # Verify
        response.json.assert_called_with()
        schema_mock.load.assert_called_with(response.json())
        assert expected_result == result

    def test_make_response_body_converter_with_unsupported_response(
            self, schema_mock_and_argument
    ):
        # Setup
        schema_mock, argument = schema_mock_and_argument
        converter = converters.MarshmallowConverter()

        # Run
        c = converter.make_response_body_converter(argument)
        result = c.convert("unsupported response")

        # Verify
        return result is None

    def test_make_response_body_converter_without_schema(self):
        # Setup
        converter = converters.MarshmallowConverter()

        # Run
        c = converter.make_response_body_converter("not a schema")

        # Verify
        assert c is None

    def test_make_string_converter(self, schema_mock_and_argument):
        # Setup
        _, argument = schema_mock_and_argument
        converter = converters.MarshmallowConverter()

        # Run
        c = converter.make_string_converter(argument, None, None)

        # Verify
        assert c is None

    def test_register(self, mocker):
        # Setup
        converter = converters.MarshmallowConverter
        old_marshmallow = converter.marshmallow

        # Run & Verify: Register when marshmallow is installed
        converter.marshmallow = True
        register_ = mocker.Mock(spec=register.Register())
        converter.register_if_necessary(register_)
        register_.register_converter_factory.assert_called_with(converter)

        # Run & Verify: Skip when marshmallow is not installed
        converter.marshmallow = None
        register_ = mocker.Mock(spec=register.Register())
        converter.register_if_necessary(register_)
        assert not register_.register_converter_factory.called

        # Rewire
        converters.MarshmallowConverter.marshmallow = old_marshmallow


class TestMap(object):
    def test_convert(self):
        # Setup
        registry = converters.ConverterFactoryRegistry(
            (converters.StandardConverter(),)
        )
        key = converters.keys.Map(converters.keys.CONVERT_TO_STRING)

        # Run
        converter = registry[key](None)
        value = converter({"hello": 1})

        # Verify
        assert value == {"hello": "1"}

    def test_eq(self):
        assert converters.keys.Map(0) == converters.keys.Map(0)
        assert not (converters.keys.Map(1) == converters.keys.Map(0))
        assert not (converters.keys.Map(1) == 1)


class TestSequence(object):
    def test_convert_with_sequence(self):
        # Setup
        registry = converters.ConverterFactoryRegistry(
            (converters.StandardConverter(),)
        )
        key = converters.keys.Sequence(converters.keys.CONVERT_TO_STRING)

        # Run
        converter = registry[key](None)
        value = converter([1, 2, 3])

        # Verify
        assert value == ["1", "2", "3"]

    def test_convert_not_sequence(self):
        # Setup
        registry = converters.ConverterFactoryRegistry(
            (converters.StandardConverter(),)
        )
        key = converters.keys.Sequence(converters.keys.CONVERT_TO_STRING)

        # Run
        converter = registry[key](None)
        value = converter("1")

        # Verify
        assert value == "1"

    def test_eq(self):
        assert converters.keys.Sequence(0) == converters.keys.Sequence(0)
        assert not (converters.keys.Sequence(1) == converters.keys.Sequence(0))
        assert not (converters.keys.Sequence(1) == 1)


class TestRegistry(object):

    @pytest.mark.parametrize(
        "converter",
        # Try with both class and instance
        (converters.StandardConverter, converters.StandardConverter())
    )
    def test_register_converter_factory_pass(self, converter):
        # Setup
        registry = register.Register()

        # Verify
        return_value = registry.register_converter_factory(converter)
        defaults = registry.get_converter_factories()
        assert return_value is converter
        assert len(defaults) == 1
        assert isinstance(defaults[0], converters.StandardConverter)

    def test_register_converter_factory_pass(self):
        # Setup
        registry = register.Register()

        # Verify failure when registered factory is not proper type.
        with pytest.raises(TypeError):
            registry.register_converter_factory(object())


class TestTypingConverter(object):
    singleton = converters.TypingConverter()
    inject_methods = pytest.mark.parametrize(
        "method, use_typing",
        [
            (singleton.make_request_body_converter, True),
            (singleton.make_request_body_converter, False),
            (singleton.make_response_body_converter, True),
            (singleton.make_response_body_converter, False)
        ]
    )

    @inject_methods
    def test_methods(self, method, use_typing):
        List, Dict = converters.typing_._get_types(use_typing)

        # Verify with sequence
        converter = method(List[str])
        assert isinstance(converter, converters.typing_.ListConverter)

        # Verify with mapping
        converter = method(Dict[str, str])
        assert isinstance(converter, converters.typing_.DictConverter)

    def test_list_converter(self):
        # Setup
        converter = converters.typing_.ListConverter(str)
        converter.set_chain(lambda x: x)

        # Verify
        output = converter([1, 2, 3])
        assert output == ["1", "2", "3"]

        # Verify with non-list: use element converter
        output = converter(1)
        assert output == "1"

    def test_dict_converter(self):
        # Setup
        converter = converters.typing_.DictConverter(int, str)
        converter.set_chain(lambda x: x)

        # Verify
        output = converter({"1": 1, "2": 2})
        assert output == {1: "1", 2: "2"}

        # Verify with non-map: use value converter
        output = converter(1)
        assert output == "1"
