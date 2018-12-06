import pytest

# Local imports
from uplink import hooks, arguments
from uplink.converters import keys


inject_args = pytest.mark.parametrize("args", (["arg1", "arg2", "arg3"],))


@pytest.fixture
def argument_mock(mocker):
    return mocker.Mock(spec=arguments.ArgumentAnnotation)


@pytest.fixture
def named_argument_mock(mocker):
    return mocker.Mock(spec=arguments.NamedArgument)


class ArgumentTestCase(object):
    @property
    def type_cls(self):
        raise NotImplementedError

    @property
    def expected_converter_key(self):
        raise NotImplementedError

    @property
    def expected_can_be_static(self):
        return True

    def test_converter_type(self):
        assert self.type_cls().converter_key == self.expected_converter_key

    def test_is_static(self):
        assert self.type_cls._can_be_static == self.expected_can_be_static

    def test_static_call(self, mocker, request_definition_builder):
        request_definition_builder = self.type_cls(request_definition_builder)
        builder = request_definition_builder.argument_handler_builder
        builder.add_annotation.assert_called_with(mocker.ANY)


class FuncDecoratorTestCase(object):
    def test_static_call_with_function(self):
        def func(a1, a2):
            return a1, a2

        output = self.type_cls(func)
        assert output is func

    def test_equals(self):
        assert isinstance(
            self.type_cls().with_value("hello"), hooks.TransactionHook
        )


class TestArgumentAnnotationHandlerBuilder(object):
    def test_from_func(self):
        def func(_):
            pass

        handler = arguments.ArgumentAnnotationHandlerBuilder.from_func(func)
        another_handler = arguments.ArgumentAnnotationHandlerBuilder.from_func(
            func
        )
        assert handler is another_handler

    @inject_args
    def test_missing_arguments(self, args):
        builder = arguments.ArgumentAnnotationHandlerBuilder(None, args, False)
        assert list(builder.missing_arguments) == args

    @inject_args
    def test_remaining_args_count(self, args):
        builder = arguments.ArgumentAnnotationHandlerBuilder(None, args, False)
        assert builder.remaining_args_count == len(args)

    @inject_args
    def test_add_annotation_without_name(self, mocker, argument_mock, args):
        builder = arguments.ArgumentAnnotationHandlerBuilder(None, args, False)
        builder.listener = mocker.stub()
        builder.add_annotation(argument_mock)
        builder.listener.assert_called_with(argument_mock)
        assert args[0] not in builder.missing_arguments

    @inject_args
    def test_add_annotation_with_name(self, mocker, argument_mock, args):
        builder = arguments.ArgumentAnnotationHandlerBuilder(None, args, False)
        builder.listener = mocker.stub()
        builder.add_annotation(argument_mock, name=args[-1])
        builder.listener.assert_called_with(argument_mock)
        assert args[-1] not in builder.missing_arguments

    @inject_args
    def test_add_named_annotation_without_name(
        self, mocker, named_argument_mock, args
    ):
        builder = arguments.ArgumentAnnotationHandlerBuilder(None, args, False)
        named_argument_mock.name = None
        builder.listener = mocker.stub()
        builder.add_annotation(named_argument_mock)
        builder.listener.assert_called_with(named_argument_mock)
        assert named_argument_mock.name == args[0]
        assert args[0] not in builder.missing_arguments

    @inject_args
    def test_add_annotation_class(self, mocker, args):
        builder = arguments.ArgumentAnnotationHandlerBuilder(None, args, False)
        builder.listener = mocker.stub()
        argument = builder.add_annotation(arguments.ArgumentAnnotation())
        builder.listener.assert_called_with(argument)
        assert args[0] not in builder.missing_arguments

    @inject_args
    def test_add_annotation_with_name_not_recognized(self, argument_mock, args):
        def dummy():
            pass

        assert -1 not in args
        builder = arguments.ArgumentAnnotationHandlerBuilder(dummy, args, False)
        with pytest.raises(arguments.ArgumentNotFound):
            builder.add_annotation(argument_mock, name=-1)

    def test_add_annotation_with_no_missing_arguments(self, argument_mock):
        def dummy():
            pass

        builder = arguments.ArgumentAnnotationHandlerBuilder(dummy, [], False)
        with pytest.raises(arguments.ExhaustedArguments):
            builder.add_annotation(argument_mock)

    def test_add_annotation_that_is_not_an_annotation(self):
        def dummy():
            pass

        builder = arguments.ArgumentAnnotationHandlerBuilder(
            dummy, ["arg1"], False
        )
        builder.add_annotation(type, "arg1")
        assert builder.remaining_args_count == 1

    @inject_args
    def test_set_annotations(self, mocker, argument_mock, args):
        builder = arguments.ArgumentAnnotationHandlerBuilder(None, args, False)
        builder.listener = mocker.stub()
        builder.set_annotations((argument_mock,))
        builder.listener.assert_called_with(argument_mock)
        assert args[0] not in builder.missing_arguments

    @inject_args
    def test_set_annotations_with_dict(self, mocker, argument_mock, args):
        builder = arguments.ArgumentAnnotationHandlerBuilder(None, args, False)
        builder.listener = mocker.stub()
        builder.set_annotations(**{args[0]: argument_mock})
        builder.listener.assert_called_with(argument_mock)
        assert args[0] not in builder.missing_arguments

    def test_is_done(self, argument_mock):
        builder = arguments.ArgumentAnnotationHandlerBuilder(
            None, ("arg1",), False
        )
        assert not builder.is_done()
        builder.add_annotation(argument_mock)
        assert builder.is_done()


class TestArgumentAnnotationHandler(object):
    def test_get_relevant_arguments(self):
        args = {"arg1": "value1"}
        annotation_handler = arguments.ArgumentAnnotationHandler(None, args)
        relevant = annotation_handler.get_relevant_arguments(args)
        assert list(relevant) == list(args.items())

    def test_handle_call(self, request_builder, mocker):
        def dummy(arg1):
            return arg1

        request_builder.get_converter.return_value = dummy
        get_call_args = mocker.patch("uplink.utils.get_call_args")
        get_call_args.return_value = {"arg1": "hello"}
        annotation = mocker.Mock(arguments.ArgumentAnnotation)
        handlers = arguments.ArgumentAnnotationHandler(
            dummy, {"arg1": annotation}
        )
        handlers.handle_call(request_builder, (), {})
        annotation.modify_request.assert_called_with(request_builder, "hello")

    @inject_args
    def test_annotations(self, args):
        annotations = ["annotation"] * len(args)
        arg_dict = dict(zip(args, annotations))
        annotation_handler = arguments.ArgumentAnnotationHandler(None, arg_dict)
        assert list(annotation_handler.annotations) == annotations


class TestArgumentAnnotation(object):
    def test_call(self, request_definition_builder):
        annotation = arguments.ArgumentAnnotation()
        return_value = annotation(request_definition_builder)
        handler_builder = request_definition_builder.argument_handler_builder
        handler_builder.add_annotation.assert_called_with(annotation)
        assert return_value is request_definition_builder


class TestTypedArgument(object):
    def test_type(self):
        assert arguments.TypedArgument("hello").type == "hello"

    def test_set_type(self):
        annotation = arguments.TypedArgument()
        assert annotation.type is None
        annotation.type = "type"
        assert annotation.type == "type"

    def test_set_type_with_type_already_set(self):
        annotation = arguments.TypedArgument("type")
        with pytest.raises(AttributeError):
            annotation.type = "new type"


class TestNamedArgument(object):
    def test_name(self):
        assert arguments.NamedArgument("name").name == "name"

    def test_set_name(self):
        annotation = arguments.NamedArgument()
        assert annotation.name is None
        annotation.name = "name"
        assert annotation.name == "name"

    def test_set_name_with_name_already_set(self):
        annotation = arguments.NamedArgument("name")
        with pytest.raises(AttributeError):
            annotation.name = "new name"


class TestPath(ArgumentTestCase):
    type_cls = arguments.Path
    expected_converter_key = keys.CONVERT_TO_STRING

    def test_modify_request_definition(self, request_definition_builder):
        arguments.Path("name").modify_request_definition(
            request_definition_builder
        )
        request_definition_builder.uri.add_variable.assert_called_with("name")

    def test_modify_request(self, request_builder):
        arguments.Path("name").modify_request(request_builder, "value")
        request_builder.url.set_variable.assert_called_with({"name": "value"})


class TestQuery(ArgumentTestCase, FuncDecoratorTestCase):
    type_cls = arguments.Query
    expected_converter_key = keys.Sequence(keys.CONVERT_TO_STRING)

    def test_modify_request(self, request_builder):
        arguments.Query("name").modify_request(request_builder, "value")
        assert request_builder.info["params"] == {"name": "value"}

    def test_modify_request_with_encoded(self, request_builder):
        arguments.Query("name", encoded=True).modify_request(
            request_builder, "value"
        )
        assert request_builder.info["params"] == "name=value"

    def test_modify_request_with_mismatched_encoding(self, request_builder):
        arguments.Query("name", encoded=True).modify_request(
            request_builder, "value"
        )
        with pytest.raises(arguments.Query.QueryStringEncodingError):
            arguments.Query("name2", encoded=False).modify_request(
                request_builder, "value2"
            )

    def test_skip_none(self, request_builder):
        arguments.Query("name").modify_request(
            request_builder, None
        )
        assert request_builder.info["params"] == {}

    def test_encode_none(self, request_builder):
        arguments.Query("name", encode_none="null").modify_request(
            request_builder, None
        )
        assert request_builder.info["params"] == {"name": "null"}

    def test_converter_key_with_encoded(self):
        query = arguments.Query("name", encoded=True)
        assert query.converter_key == keys.CONVERT_TO_STRING

    def test_converter_type(self):
        query = arguments.Query("name", encoded=False)
        assert query.converter_key == keys.Sequence(keys.CONVERT_TO_STRING)


class TestQueryMap(ArgumentTestCase, FuncDecoratorTestCase):
    type_cls = arguments.QueryMap
    expected_converter_key = keys.Map(TestQuery.expected_converter_key)

    def test_modify_request(self, request_builder):
        arguments.QueryMap().modify_request(request_builder, {"hello": "world"})
        assert request_builder.info["params"] == {"hello": "world"}

    def test_modify_request_with_encoded(self, request_builder):
        arguments.QueryMap(encoded=True).modify_request(
            request_builder, {"name": "value"}
        )
        assert request_builder.info["params"] == "name=value"

    def test_converter_key_with_encoded(self):
        query = arguments.QueryMap(encoded=True)
        assert query.converter_key == keys.Map(keys.CONVERT_TO_STRING)

    def test_converter_type(self):
        query = arguments.QueryMap(encoded=False)
        assert query.converter_key == keys.Map(
            keys.Sequence(keys.CONVERT_TO_STRING)
        )


class TestHeader(ArgumentTestCase, FuncDecoratorTestCase):
    type_cls = arguments.Header
    expected_converter_key = keys.CONVERT_TO_STRING

    def test_modify_request(self, request_builder):
        arguments.Header("hello").modify_request(request_builder, "world")
        assert request_builder.info["headers"] == {"hello": "world"}


class TestHeaderMap(ArgumentTestCase, FuncDecoratorTestCase):
    type_cls = arguments.HeaderMap
    expected_converter_key = keys.Map(TestHeader.expected_converter_key)

    def test_modify_request(self, request_builder):
        arguments.HeaderMap().modify_request(
            request_builder, {"hello": "world"}
        )
        assert request_builder.info["headers"] == {"hello": "world"}


class TestField(ArgumentTestCase):
    type_cls = arguments.Field
    expected_converter_key = keys.CONVERT_TO_REQUEST_BODY

    def test_modify_request(self, request_builder):
        arguments.Field("hello").modify_request(request_builder, "world")
        assert request_builder.info["data"]["hello"] == "world"

    def test_modify_request_failure(self, request_builder):
        request_builder.info["data"] = object()
        with pytest.raises(arguments.Field.FieldAssignmentFailed):
            arguments.Field("hello").modify_request(request_builder, "world")


class TestFieldMap(ArgumentTestCase):
    type_cls = arguments.FieldMap
    expected_converter_key = keys.Map(TestField.expected_converter_key)

    def test_modify_request(self, request_builder):
        arguments.FieldMap().modify_request(request_builder, {"hello": "world"})
        assert request_builder.info["data"] == {"hello": "world"}

    def test_modify_request_failure(self, request_builder):
        request_builder.info["data"] = object()
        with pytest.raises(arguments.FieldMap.FieldMapUpdateFailed):
            arguments.FieldMap().modify_request(request_builder, {})


class TestPart(ArgumentTestCase):
    type_cls = arguments.Part
    expected_converter_key = keys.CONVERT_TO_REQUEST_BODY

    def test_modify_request(self, request_builder):
        arguments.Part("hello").modify_request(request_builder, "world")
        assert request_builder.info["files"] == {"hello": "world"}


class TestPartMap(ArgumentTestCase):
    type_cls = arguments.PartMap
    expected_converter_key = keys.Map(TestPart.expected_converter_key)

    def test_modify_request(self, request_builder):
        arguments.PartMap().modify_request(request_builder, {"hello": "world"})
        assert request_builder.info["files"] == {"hello": "world"}


class TestBody(ArgumentTestCase):
    type_cls = arguments.Body
    expected_converter_key = keys.CONVERT_TO_REQUEST_BODY

    def test_modify_request(self, request_builder):
        # Verify with dict
        arguments.Body().modify_request(request_builder, {"hello": "world"})
        assert request_builder.info["data"] == {"hello": "world"}

        # Verify with non-mapping
        body = object()
        arguments.Body().modify_request(request_builder, body)
        assert request_builder.info["data"] is body


class TestUrl(ArgumentTestCase):
    type_cls = arguments.Url
    expected_converter_key = keys.CONVERT_TO_STRING

    def test_modify_request_definition(self, request_definition_builder):
        arguments.Url().modify_request_definition(request_definition_builder)
        assert request_definition_builder.uri.is_dynamic

    def test_modify_request_definition_failure(
        self, mocker, request_definition_builder
    ):
        is_dynamic_mock = mocker.PropertyMock(side_effect=ValueError())
        type(request_definition_builder.uri).is_dynamic = is_dynamic_mock
        request_definition_builder.__name__ = "dummy"
        with pytest.raises(arguments.Url.DynamicUrlAssignmentFailed):
            arguments.Url().modify_request_definition(
                request_definition_builder
            )

    def test_modify_request(self, request_builder):
        arguments.Url().modify_request(request_builder, "/some/path")
        assert request_builder.url == "/some/path"
