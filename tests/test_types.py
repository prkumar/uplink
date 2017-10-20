import pytest

# Local imports
from uplink import converter, types


inject_args = pytest.mark.parametrize(
    "args", (["arg1", "arg2", "arg3"],)
)


@pytest.fixture
def argument_mock(mocker):
    return mocker.Mock(spec=types.ArgumentAnnotation)


@pytest.fixture
def named_argument_mock(mocker):
    return mocker.Mock(spec=types.NamedArgument)


class ArgumentTestCase(object):

    @property
    def type_cls(self):
        raise NotImplementedError

    @property
    def expected_converter_type(self):
        raise NotImplementedError

    @property
    def expected_can_be_static(self):
        return True

    def test_converter_type(self):
        assert self.type_cls().converter_type == self.expected_converter_type

    def test_is_static(self):
        assert self.type_cls.can_be_static == self.expected_can_be_static


class TestArgumentAnnotationHandlerBuilder(object):
    
    @inject_args
    def test_missing_arguments(self, args):
        builder = types.ArgumentAnnotationHandlerBuilder(None, args, False)
        assert list(builder.missing_arguments) == args
    
    @inject_args
    def test_remaining_args_count(self, args):
        builder = types.ArgumentAnnotationHandlerBuilder(None, args, False)
        assert builder.remaining_args_count == len(args)

    @inject_args
    def test_add_annotation_without_name(self, argument_mock, args):
        builder = types.ArgumentAnnotationHandlerBuilder(None, args, False)
        builder.add_annotation(argument_mock)
        argument_mock.modify_request_definition.assert_called_with(
            builder.request_definition_builder
        )
        assert args[0] not in builder.missing_arguments

    @inject_args
    def test_add_annotation_with_name(self, argument_mock, args):
        builder = types.ArgumentAnnotationHandlerBuilder(None, args, False)
        builder.add_annotation(argument_mock, name=args[-1])
        argument_mock.modify_request_definition.assert_called_with(
            builder.request_definition_builder
        )
        assert args[-1] not in builder.missing_arguments

    @inject_args
    def test_add_named_annotation_without_name(self, named_argument_mock, args):
        builder = types.ArgumentAnnotationHandlerBuilder(None, args, False)
        named_argument_mock.name = None
        builder.add_annotation(named_argument_mock)
        named_argument_mock.modify_request_definition.assert_called_with(
            builder.request_definition_builder
        )
        assert named_argument_mock.name == args[0]
        assert args[0] not in builder.missing_arguments

    @inject_args
    def test_add_annotation_class(self, argument_mock, args):
        builder = types.ArgumentAnnotationHandlerBuilder(None, args, False)
        argument = builder.add_annotation(type(argument_mock))
        argument.modify_request_definition.assert_called_with(
            builder.request_definition_builder
        )
        assert args[0] not in builder.missing_arguments

    @inject_args
    def test_add_annotation_with_name_not_recognized(self, argument_mock, args):
        def dummy(): pass
        assert -1 not in args
        builder = types.ArgumentAnnotationHandlerBuilder(dummy, args, False)
        with pytest.raises(types.ArgumentNotFound):
            builder.add_annotation(argument_mock, name=-1)

    def test_add_annotation_with_no_missing_arguments(self, argument_mock):
        def dummy(): pass
        builder = types.ArgumentAnnotationHandlerBuilder(dummy, [], False)
        with pytest.raises(types.ExhaustedArguments):
            builder.add_annotation(argument_mock)

    @inject_args
    def test_set_annotations(self, argument_mock, args):
        builder = types.ArgumentAnnotationHandlerBuilder(None, args, False)
        builder.set_annotations((argument_mock,))
        argument_mock.modify_request_definition.assert_called_with(
            builder.request_definition_builder
        )
        assert args[0] not in builder.missing_arguments

    @inject_args
    def test_set_annotations_with_dict(self, argument_mock, args):
        builder = types.ArgumentAnnotationHandlerBuilder(None, args, False)
        builder.set_annotations(**{args[0]: argument_mock})
        argument_mock.modify_request_definition.assert_called_with(
            builder.request_definition_builder
        )
        assert args[0] not in builder.missing_arguments

    @inject_args
    def test_auto_fill_when_not_done(self, request_definition_builder, args):
        request_definition_builder.uri.remaining_variables = args
        builder = types.ArgumentAnnotationHandlerBuilder(None, args, False)
        builder.set_request_definition_builder(request_definition_builder)
        handler = builder.build()
        types_ = map(type, handler.annotations)
        assert list(types_) == ([types.Path] * len(args))
        names = [argument.name for argument in handler.annotations]
        assert names == args

    def test_auto_fill_when_not_done_fails(self, request_definition_builder):
        request_definition_builder.uri.remaining_variables = []
        builder = types.ArgumentAnnotationHandlerBuilder(None, ["arg1"], False)
        builder.set_request_definition_builder(request_definition_builder)
        with pytest.raises(types.MissingArgumentAnnotations):
            builder.build()


class TestArgumentAnnotationHandler(object):

    @inject_args
    def test_get_relevant_arguments(self, args):
        annotation_handler = types.ArgumentAnnotationHandler(None, args)
        relevant = annotation_handler.get_relevant_arguments(args[1:])
        assert list(relevant) == args[1:]

    def test_handle_call(self, request_builder, converter_mock, mocker):
        def dummy(arg1): return arg1
        request_builder.get_converter.return_value = converter_mock
        converter_mock.convert = dummy
        get_call_args = mocker.patch("uplink.utils.get_call_args")
        get_call_args.return_value = {"arg1": "hello"}
        annotation = mocker.Mock(types.ArgumentAnnotation)
        handlers = types.ArgumentAnnotationHandler(
            dummy, {"arg1": annotation}
        )
        handlers.handle_call(request_builder, (), {})
        annotation.modify_request.assert_called_with(request_builder, "hello")


class TestArgumentAnnotation(object):

    def test_call(self, request_definition_builder):
        annotation = types.ArgumentAnnotation()
        return_value = annotation(request_definition_builder)
        handler_builder = request_definition_builder.argument_handler_builder
        handler_builder.add_annotation.assert_called_with(annotation)
        assert return_value is request_definition_builder


class TestTypedArgument(object):

    def test_type(self):
        assert types.TypedArgument("hello").type == "hello"


class TestNamedArgument(object):

    def test_name(self):
        assert types.NamedArgument("name").name == "name"

    def test_set_name(self):
        annotation = types.NamedArgument()
        assert annotation.name is None
        annotation.name = "name"
        assert annotation.name == "name"

    def test_set_name_with_name_already_set(self):
        annotation = types.NamedArgument("name")
        with pytest.raises(AttributeError):
            annotation.name = "new name"


class TestPath(ArgumentTestCase):
    type_cls = types.Path
    expected_converter_type = converter.CONVERT_TO_STRING

    def test_modify_request_definition(self, request_definition_builder):
        types.Path("name").modify_request_definition(request_definition_builder)
        request_definition_builder.uri.add_variable.assert_called_with("name")

    def test_modify_request(self, request_builder):
        types.Path("name").modify_request(request_builder, "value")
        request_builder.uri.set_variable.assert_called_with({"name": "value"})


class TestQuery(ArgumentTestCase):
    type_cls = types.Query
    expected_converter_type = converter.CONVERT_TO_REQUEST_BODY

    def test_modify_request(self, request_builder):
        types.Query("name").modify_request(request_builder, "value")
        assert request_builder.info["params"] == {"name": "value"}


class TestQueryMap(ArgumentTestCase):
    type_cls = types.QueryMap
    expected_converter_type = converter.Map(converter.CONVERT_TO_REQUEST_BODY)

    def test_modify_request(self, request_builder):
        types.QueryMap().modify_request(request_builder, {"hello": "world"})
        assert request_builder.info["params"] == {"hello": "world"}


class TestHeader(ArgumentTestCase):
    type_cls = types.Header
    expected_converter_type = converter.CONVERT_TO_STRING

    def test_modify_request(self, request_builder):
        types.Header("hello").modify_request(request_builder, "world")
        assert request_builder.info["headers"] == {"hello": "world"}


class TestHeaderMap(ArgumentTestCase):
    type_cls = types.HeaderMap
    expected_converter_type = converter.Map(converter.CONVERT_TO_STRING)

    def test_modify_request(self, request_builder):
        types.HeaderMap().modify_request(request_builder, {"hello": "world"})
        assert request_builder.info["headers"] == {"hello": "world"}


class TestField(ArgumentTestCase):
    type_cls = types.Field
    expected_converter_type = converter.CONVERT_TO_STRING

    def test_modify_request(self, request_builder):
        types.Field("hello").modify_request(request_builder, "world")
        assert request_builder.info["data"]["hello"] == "world"

    def test_modify_request_failure(self, request_builder):
        request_builder.info["data"] = object()
        with pytest.raises(types.Field.FieldAssignmentFailed):
            types.Field("hello").modify_request(request_builder, "world")


class TestFieldMap(ArgumentTestCase):
    type_cls = types.FieldMap
    expected_converter_type = converter.Map(converter.CONVERT_TO_STRING)

    def test_modify_request(self, request_builder):
        types.FieldMap().modify_request(request_builder, {"hello": "world"})
        assert request_builder.info["data"] == {"hello": "world"}

    def test_modify_request_failure(self, request_builder):
        request_builder.info["data"] = object()
        with pytest.raises(types.FieldMap.FieldMapUpdateFailed):
            types.FieldMap().modify_request(request_builder, {})


class TestPart(ArgumentTestCase):
    type_cls = types.Part
    expected_converter_type = converter.CONVERT_TO_REQUEST_BODY

    def test_modify_request(self, request_builder):
        types.Part("hello").modify_request(request_builder, "world")
        assert request_builder.info["files"] == {"hello": "world"}


class TestPartMap(ArgumentTestCase):
    type_cls = types.PartMap
    expected_converter_type = converter.Map(converter.CONVERT_TO_REQUEST_BODY)

    def test_modify_request(self, request_builder):
        types.PartMap().modify_request(request_builder, {"hello": "world"})
        assert request_builder.info["files"] == {"hello": "world"}


class TestBody(ArgumentTestCase):
    type_cls = types.Body
    expected_converter_type = converter.CONVERT_TO_REQUEST_BODY

    def test_modify_request(self, request_builder):
        types.Body().modify_request(request_builder, {"hello": "world"})
        assert request_builder.info["data"] == {"hello": "world"}


class TestUrl(ArgumentTestCase):
    type_cls = types.Url
    expected_converter_type = converter.CONVERT_TO_STRING

    def test_modify_request_definition(self, request_definition_builder):
        types.Url().modify_request_definition(request_definition_builder)
        assert request_definition_builder.uri.is_dynamic

    def test_modify_request_definition_failure(self,
                                               mocker,
                                               request_definition_builder):
        is_dynamic_mock = mocker.PropertyMock(side_effect=ValueError())
        type(request_definition_builder.uri).is_dynamic = is_dynamic_mock
        request_definition_builder.__name__ = "dummy"
        with pytest.raises(types.Url.DynamicUrlAssignmentFailed):
            types.Url().modify_request_definition(request_definition_builder)

    def test_modify_request(self, request_builder):
        types.Url().modify_request(request_builder, "/some/path")
        assert request_builder.uri == "/some/path"
