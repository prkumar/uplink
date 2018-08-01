# Standard library imports
import collections

# Third party imports
import pytest

# Local imports
from uplink import decorators, interfaces


@pytest.fixture
def method_annotation():
    return decorators.MethodAnnotation()


@pytest.fixture
def method_annotation_mock(mocker):
    return mocker.Mock(spec=decorators.MethodAnnotation)


@pytest.fixture
def method_handler_builder():
    return decorators.MethodAnnotationHandlerBuilder()


class TestMethodAnnotationHandlerBuilder(object):
    def test_add_annotation(
        self, mocker, method_handler_builder, method_annotation_mock
    ):
        method_handler_builder.listener = mocker.stub()
        method_handler_builder.add_annotation(method_annotation_mock)
        method_handler_builder.listener.assert_called_with(
            method_annotation_mock
        )
        annotations = method_handler_builder.build().annotations
        assert list(annotations) == [method_annotation_mock]

    def test_build(self, method_handler_builder, method_annotation):
        method_handler_builder.add_annotation(method_annotation)
        handler = method_handler_builder.build()
        assert list(handler.annotations) == [method_annotation]

    def test_class_level_appears_before_method_level_annotations(
        self, method_handler_builder
    ):
        method_level1 = decorators.MethodAnnotation()
        method_level2 = decorators.MethodAnnotation()
        class_level1 = decorators.MethodAnnotation()
        class_level2 = decorators.MethodAnnotation()
        method_handler_builder.add_annotation(method_level1)
        method_handler_builder.add_annotation(method_level2)
        method_handler_builder.add_annotation(class_level1, is_class=True)
        method_handler_builder.add_annotation(class_level2, is_class=True)
        handler = method_handler_builder.build()
        assert list(handler.annotations) == [
            class_level1,
            class_level2,
            method_level1,
            method_level2,
        ]


class TestMethodAnnotationHandler(object):
    def test_handle_builder(self, request_builder, method_annotation_mock):
        handler = decorators.MethodAnnotationHandler([method_annotation_mock])
        handler.handle_builder(request_builder)
        method_annotation_mock.modify_request.assert_called_with(
            request_builder
        )

    def test_annotations(self, method_annotation_mock):
        handler = decorators.MethodAnnotationHandler([method_annotation_mock])
        assert list(handler.annotations) == [method_annotation_mock]


class TestMethodAnnotation(object):
    class FakeMethodAnnotation(decorators.MethodAnnotation):
        _can_be_static = True

    def test_call_with_class(
        self, method_annotation, request_definition_builder
    ):
        class Class(interfaces.Consumer):
            builder = request_definition_builder

        method_annotation(Class)
        builder = request_definition_builder.method_handler_builder
        builder.add_annotation.assert_called_with(
            method_annotation, is_class=True
        )

    def test_static_call_with_class(self, mocker, request_definition_builder):
        class Class(interfaces.Consumer):
            builder = request_definition_builder

        self.FakeMethodAnnotation(Class)
        builder = request_definition_builder.method_handler_builder
        builder.add_annotation.assert_called_with(mocker.ANY, is_class=True)

    def test_call_with_builder(
        self, method_annotation, request_definition_builder
    ):
        method_annotation(request_definition_builder)
        builder = request_definition_builder.method_handler_builder
        builder.add_annotation.assert_called_with(method_annotation)

    def test_static_call_with_builder(self, mocker, request_definition_builder):
        self.FakeMethodAnnotation(request_definition_builder)
        builder = request_definition_builder.method_handler_builder
        builder.add_annotation.assert_called_with(mocker.ANY)

    def test_method_in_http_method_blacklist(self, request_definition_builder):
        class DummyAnnotation(decorators.MethodAnnotation):
            _http_method_blacklist = ["GET"]

        request_definition_builder.method = "GET"
        assert not DummyAnnotation.supports_http_method(
            request_definition_builder.method
        )

    def test_method_not_in_http_method_blacklist(
        self, request_definition_builder
    ):
        class DummyAnnotation(decorators.MethodAnnotation):
            _http_method_whitelist = ["POST"]

        request_definition_builder.method = "POST"
        request_definition_builder.__name__ = "dummy"
        assert DummyAnnotation().supports_http_method(
            request_definition_builder.method
        )

    def test_call_with_child_class(
        self, method_annotation, request_definition_builder
    ):
        class Parent(object):
            builder = request_definition_builder

        class Child(Parent):
            pass

        # Method annotation should not decorate RequestDefinitionBuilder
        # attribute of parent class (e.g., `Parent.builder`).
        method_annotation(Child)
        builder = request_definition_builder.method_handler_builder
        assert not builder.add_annotation.called


# TODO: Refactor test cases for method annotations into test case class.


def test_headers(request_builder):
    headers = decorators.headers({"key_1": "value_1"})
    headers.modify_request(request_builder)
    assert request_builder.info["headers"] == {"key_1": "value_1"}

    headers_str = decorators.headers("key_1: value_1")
    headers_str.modify_request(request_builder)
    assert request_builder.info["headers"] == {"key_1": "value_1"}

    headers_lst = decorators.headers(["key_1: value_1", "key_2: value_2"])
    headers_lst.modify_request(request_builder)
    header = {"key_1": "value_1", "key_2": "value_2"}
    assert request_builder.info["headers"] == header


def test_params(request_builder):
    params = decorators.params({"param": "value"})
    params.modify_request(request_builder)
    assert request_builder.info["params"] == {"param": "value"}


def test_params_with_string(request_builder):
    params_with_str = decorators.params("param1=value1&param2=value2")
    params_with_str.modify_request(request_builder)
    assert request_builder.info["params"] == {
        "param1": "value1",
        "param2": "value2",
    }


def test_params_with_list(request_builder):
    params_list = decorators.params(["param1=value1", "param2=value2"])
    params_list.modify_request(request_builder)
    assert request_builder.info["params"] == {
        "param1": "value1",
        "param2": "value2",
    }


def test_form_url_encoded(request_builder):
    form_url_encoded = decorators.form_url_encoded()
    form_url_encoded.modify_request(request_builder)
    assert "headers" not in request_builder.info


def test_multipart(request_builder):
    multipart = decorators.multipart()
    multipart.modify_request(request_builder)
    assert "headers" not in request_builder.info


def test_json(request_builder):
    json = decorators.json()

    # Verify that we add the hook
    json.modify_request(request_builder)
    request_builder.add_transaction_hook.assert_called_with(json._hook)

    # Verify
    request_builder.info["data"] = {"field_name": "field_value"}
    json.set_json_body(request_builder)
    assert request_builder.info["json"] == {"field_name": "field_value"}
    assert len(request_builder.info["json"]) == 1

    # Check delete
    del request_builder.info["json"]["field_name"]
    assert len(request_builder.info["json"]) == 0
    assert "data" not in request_builder.info

    # Verify nested attribute
    request_builder.info["data"] = {("outer", "inner"): "inner_value"}
    json.set_json_body(request_builder)
    assert request_builder.info["json"] == {"outer": {"inner": "inner_value"}}
    assert "data" not in request_builder.info

    # Verify that error is raised when path is empty
    request_builder.info["data"] = {(): "value"}
    with pytest.raises(ValueError):
        json.set_json_body(request_builder)

    # Verify that error is raised when paths conflict
    request_builder.info["data"] = body = collections.OrderedDict()
    body["key"] = "outer"
    body["key", "inner"] = "inner value"
    with pytest.raises(ValueError):
        json.set_json_body(request_builder)


def test_json_list(request_builder):
    json = decorators.json()

    # Verify nested attribute
    request_builder.info["data"] = ["one", "two", "three"]
    json.set_json_body(request_builder)
    assert request_builder.info["json"] == ["one", "two", "three"]
    assert "data" not in request_builder.info


def test_timeout(request_builder):
    timeout = decorators.timeout(60)
    timeout.modify_request(request_builder)
    request_builder.info["timeout"] == 60


def test_args(request_definition_builder):
    args = decorators.args(str, str, name=str)
    args.modify_request_definition(request_definition_builder)
    builder = request_definition_builder.argument_handler_builder
    builder.set_annotations.assert_called_with((str, str), name=str)


def test_args_decorate_function(mocker):
    handler = mocker.Mock(spec=["set_annotations"])

    @classmethod
    def patched(*_):
        return handler

    mocker.patch(
        "uplink.arguments.ArgumentAnnotationHandlerBuilder.from_func", patched
    )
    args = decorators.args(str, str, name=str)
    func = mocker.stub()
    args(func)
    handler.set_annotations.assert_called_with((str, str), name=str)


def test_args_call_old(request_definition_builder):
    annotation = decorators.args(str, str, name=str)
    annotation(request_definition_builder)
    handler = request_definition_builder.method_handler_builder
    handler.add_annotation.assert_called_with(annotation)


def test_response_handler(request_builder):
    @decorators.response_handler
    def handler(response):
        return response

    handler.modify_request(request_builder)
    request_builder.add_transaction_hook.assert_called_with(handler)


def test_error_handler(request_builder):
    @decorators.error_handler
    def handler(*_):
        return True

    handler.modify_request(request_builder)
    request_builder.add_transaction_hook.assert_called_with(handler)


def test_inject(request_builder, transaction_hook_mock):
    handler = decorators.inject(transaction_hook_mock)
    handler.modify_request(request_builder)
    request_builder.add_transaction_hook.assert_called_with(handler)
