# Third party imports
import pytest

# Local imports
from uplink import commands, converters, arguments, utils


class TestHttpMethodFactory(object):
    def test_call_as_decorator_with_no_args(self):
        @commands.HttpMethodFactory(None)
        def func():
            pass

        assert isinstance(func, commands.RequestDefinitionBuilder)

    def test_call_as_decorator_with_args(self):
        method_factory = commands.HttpMethodFactory(None)

        @method_factory(None)
        def func():
            pass

        assert isinstance(func, commands.RequestDefinitionBuilder)


class TestHttpMethod(object):
    def test_call(self, mocker, annotation_mock):
        # Setup
        def func():
            pass

        sig = utils.Signature(
            args=["self", "arg1", "arg2"],
            annotations={"arg1": annotation_mock},
            return_annotation=None,
        )
        mocker.patch("uplink.utils.get_arg_spec").return_value = sig

        http_method = commands.HttpMethod("METHOD", uri="/{hello}")
        builder = http_method(func)
        assert isinstance(builder, commands.RequestDefinitionBuilder)
        assert builder.__name__ == func.__name__
        assert builder.method == "METHOD"
        assert list(builder.uri.remaining_variables) == ["hello"]

        missing_arguments = builder.argument_handler_builder.missing_arguments
        expected_missing = set(sig.args[1:]) - set(sig.annotations.keys())
        assert set(missing_arguments) == expected_missing

    def test_call_with_return_annotation(self, mocker):
        # Setup
        def func():
            pass

        sig = utils.Signature(
            args=[], annotations={}, return_annotation="return_annotation"
        )
        mocker.patch("uplink.utils.get_arg_spec").return_value = sig
        returns = mocker.patch("uplink.returns.schema")
        http_method = commands.HttpMethod("METHOD", uri="/{hello}")
        http_method(func)

        # Verify: build is wrapped with decorators.returns
        returns.assert_called_with(sig.return_annotation)

    def test_call_with_args(self, mocker, annotation_mock):
        # Setup
        def func():
            pass

        args = mocker.patch("uplink.decorators.args")

        # Verify: using sequence
        http_method = commands.HttpMethod(
            "METHOD", uri="/{hello}", args=(annotation_mock,)
        )
        http_method(func)
        args.assert_called_with(annotation_mock)

        # Verify: using mapping
        http_method = commands.HttpMethod(
            "METHOD", uri="/{hello}", args={"arg1": "value"}
        )
        http_method(func)
        args.assert_called_with(arg1="value")


class TestURIDefinitionBuilder(object):
    def test_is_static(self):
        assert not commands.URIDefinitionBuilder(None).is_static

    def test_is_dynamic_setter(self):
        uri = commands.URIDefinitionBuilder(None)
        assert not uri.is_dynamic
        uri.is_dynamic = True
        assert uri.is_dynamic

    def test_is_dynamic_setter_fails_when_is_static(self):
        uri = commands.URIDefinitionBuilder(True)
        assert uri.is_static
        with pytest.raises(ValueError):
            uri.is_dynamic = True

    def test_remaining_variables(self):
        uri = commands.URIDefinitionBuilder("/path/with/{variable}")
        assert uri.remaining_variables == set(["variable"])

    def test_add_variable(self):
        uri = commands.URIDefinitionBuilder("/path/with/{variable}")
        assert "variable" in uri.remaining_variables
        uri.add_variable("variable")
        assert "variable" not in uri.remaining_variables

    def test_add_variable_raise_error_when_name_is_not_in_static_path(self):
        uri = commands.URIDefinitionBuilder("/static/path")
        with pytest.raises(ValueError):
            uri.add_variable("variable")

    def test_build(self):
        uri = commands.URIDefinitionBuilder("/static/path")
        assert uri.build() == "/static/path"

    def test_build_fails_when_variable_remain_in_uri(self):
        uri = commands.URIDefinitionBuilder("/path/with/{variable}")
        with pytest.raises(commands.MissingUriVariables):
            uri.build()


class TestRequestDefinitionBuilder(object):
    def test_method_handler_builder_getter(
        self, annotation_handler_builder_mock
    ):
        builder = commands.RequestDefinitionBuilder(
            None,
            None,
            type(annotation_handler_builder_mock)(),
            annotation_handler_builder_mock,
        )
        assert builder.method_handler_builder is annotation_handler_builder_mock

    def test_build(self, mocker, annotation_handler_builder_mock):
        argument_handler_builder = type(annotation_handler_builder_mock)()
        method_handler_builder = annotation_handler_builder_mock
        uri_definition_builder = mocker.Mock(spec=commands.URIDefinitionBuilder)
        builder = commands.RequestDefinitionBuilder(
            "method",
            uri_definition_builder,
            argument_handler_builder,
            method_handler_builder,
        )
        definition = builder.build()
        assert isinstance(definition, commands.RequestDefinition)
        assert uri_definition_builder.build.called
        assert argument_handler_builder.build.called
        assert method_handler_builder.build.called

    def test_auto_fill_when_not_done(
        self, mocker, annotation_handler_builder_mock
    ):
        # Setup
        argument_handler_builder = mocker.Mock(
            stub=arguments.ArgumentAnnotationHandlerBuilder
        )
        method_handler_builder = annotation_handler_builder_mock
        uri_definition_builder = mocker.Mock(spec=commands.URIDefinitionBuilder)
        builder = commands.RequestDefinitionBuilder(
            "method",
            uri_definition_builder,
            argument_handler_builder,
            method_handler_builder,
        )

        # Setup success condition
        argument_handler_builder.is_done.return_value = False
        argument_handler_builder.missing_arguments = ["arg1"]
        uri_definition_builder.remaining_variables = ["arg1"]

        # Verify
        builder.build()
        argument_handler_builder.set_annotations.assert_called_with(
            {"arg1": arguments.Path}
        )

    def test_auto_fill_when_not_done_fails(
        self, mocker, annotation_handler_builder_mock
    ):
        # Setup
        argument_handler_builder = annotation_handler_builder_mock
        method_handler_builder = annotation_handler_builder_mock
        uri_definition_builder = mocker.Mock(spec=commands.URIDefinitionBuilder)
        builder = commands.RequestDefinitionBuilder(
            "method",
            uri_definition_builder,
            argument_handler_builder,
            method_handler_builder,
        )

        # Setup fail condition: Argument is missing annotation
        argument_handler_builder.is_done.return_value = False
        argument_handler_builder.missing_arguments = ["arg1"]
        uri_definition_builder.remaining_variables = []

        # Verify
        with pytest.raises(commands.MissingArgumentAnnotations):
            builder.build()


class TestRequestDefinition(object):
    def test_argument_annotations(self, annotation_handler_mock):
        annotation_handler_mock.annotations = ["arg1", "arg2"]
        definition = commands.RequestDefinition(
            None, None, annotation_handler_mock, None
        )
        assert list(definition.argument_annotations) == ["arg1", "arg2"]

    def test_method_annotations(self, annotation_handler_mock):
        annotation_handler_mock.annotations = ["arg1", "arg2"]
        definition = commands.RequestDefinition(
            None, None, None, annotation_handler_mock
        )
        assert list(definition.method_annotations) == ["arg1", "arg2"]

    def test_define_request(self, request_builder, mocker):
        method = "method"
        uri = "uri"
        definition = commands.RequestDefinition(
            method, uri, mocker.Mock(), mocker.Mock()
        )
        definition.define_request(request_builder, (), {})
        assert request_builder.method == method
        assert request_builder.url == uri

    def test_make_converter_registry(self, annotation_handler_mock):
        definition = commands.RequestDefinition(
            "method", "uri", annotation_handler_mock, annotation_handler_mock
        )
        annotation_handler_mock.annotations = ("annotation",)
        registry = definition.make_converter_registry(())
        assert isinstance(registry, converters.ConverterFactoryRegistry)
