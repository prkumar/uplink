import pytest

# Local imports
from uplink import decorators


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

    def test_add_annotation(self,
                            method_handler_builder,
                            method_annotation_mock):
        method_handler_builder.add_annotation(method_annotation_mock)
        method_annotation_mock.modify_request_definition.assert_called_with(
            method_handler_builder.request_definition_builder
        )
        annotations = method_handler_builder.build().annotations
        assert list(annotations) == [method_annotation_mock]

    def test_build(self, method_handler_builder, method_annotation):
        method_handler_builder.add_annotation(method_annotation)
        handler = method_handler_builder.build()
        assert list(handler.annotations) == [method_annotation]


class TestMethodAnnotationHandler(object):

    def test_handle_builder(self, request_builder, method_annotation_mock):
        handler = decorators.MethodAnnotationHandler(
            [method_annotation_mock]
        )
        handler.handle_builder(request_builder)
        method_annotation_mock.modify_request.assert_called_with(
            request_builder
        )


class TestMethodAnnotation(object):

    def test_call_with_class(self,
                             method_annotation,
                             request_definition_builder):
        class Class(object):
            builder = request_definition_builder

        method_annotation(Class)
        builder = request_definition_builder.method_handler_builder
        builder.add_annotation.assert_called_with(method_annotation)

    def test_call_with_builder(self,
                               method_annotation,
                               request_definition_builder):
        method_annotation(request_definition_builder)
        builder = request_definition_builder.method_handler_builder
        builder.add_annotation.assert_called_with(method_annotation)

    def test_method_in_http_method_whitelist(self,
                                             method_annotation,
                                             request_definition_builder):
        request_definition_builder.method = "GET"
        method_annotation.http_method_whitelist = ["GET"]
        method_annotation.modify_request_definition(
            request_definition_builder
        )
        assert True

    def test_method_not_in_http_method_whitelist(self,
                                                 method_annotation,
                                                 request_definition_builder):
        request_definition_builder.method = "POST"
        request_definition_builder.__name__ = "dummy"
        method_annotation.http_method_whitelist = ["GET"]
        with pytest.raises(decorators.HttpMethodNotSupport):
            method_annotation.modify_request_definition(
                request_definition_builder
            )


def test_headers(request_builder):
    headers = decorators.headers({"key_1": "value_1"})
    headers.modify_request(request_builder)
    assert request_builder.info["headers"] == {"key_1": "value_1"}


def test_form_url_encoded(request_builder):
    form_url_encoded = decorators.form_url_encoded()
    form_url_encoded.modify_request(request_builder)
    assert "headers" not in request_builder.info


def test_multipart(request_builder):
    multipart = decorators.multipart()
    multipart.modify_request(request_builder)
    assert "headers" not in request_builder.info


def test_json(request_builder):
    multipart = decorators.json()
    request_builder.info["data"] = {"field_name": "field_value"}
    multipart.modify_request(request_builder)
    assert request_builder.info["json"] == {"field_name": "field_value"}
    assert "data" not in request_builder.info


def test_timeout(request_builder):
    timeout = decorators.timeout(60)
    timeout.modify_request(request_builder)
    request_builder.info["timeout"] == 60


def test_returns(request_builder):
    returns = decorators.returns(str)
    returns.modify_request(request_builder)
    request_builder.set_return_type.assert_called_with(str)


def test_args(request_definition_builder):
    args = decorators.args(str, str, name=str)
    args.modify_request_definition(request_definition_builder)
    builder = request_definition_builder.argument_handler_builder
    builder.set_annotations.assert_called_with((str, str), name=str)
