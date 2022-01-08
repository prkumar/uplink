# Local imports
from uplink import returns


def test_returns(request_builder):
    custom = returns(str)
    request_builder.get_converter.return_value = str
    request_builder.return_type = returns.ReturnType.with_decorator(
        None, custom
    )
    custom.modify_request(request_builder)
    assert request_builder.return_type(2) == "2"


def test_returns_with_multiple_decorators(request_builder, mocker):
    decorator1 = returns(str)
    decorator2 = returns.json()
    request_builder.get_converter.return_value = str
    first_type = returns.ReturnType.with_decorator(None, decorator1)
    second_type = (
        request_builder.return_type
    ) = returns.ReturnType.with_decorator(first_type, decorator2)

    # Verify that the return type doesn't change after being handled by first decorator
    decorator1.modify_request(request_builder)
    assert request_builder.return_type is second_type

    # Verify that the second decorator does handle the return type
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"key": "value"}
    decorator2.modify_request(request_builder)
    assert request_builder.return_type(mock_response) == str(
        mock_response.json()
    )


def test_returns_json(request_builder, mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"key": "value"}
    request_builder.get_converter.return_value = str
    returns_json = returns.json(str, ())
    request_builder.return_type = returns.ReturnType.with_decorator(
        None, returns_json
    )
    returns_json.modify_request(request_builder)
    assert isinstance(request_builder.return_type, returns.ReturnType)
    assert callable(request_builder.return_type)
    assert request_builder.return_type(mock_response) == str(
        mock_response.json()
    )

    # Verify: Idempotent
    returns_json.modify_request(request_builder)
    assert isinstance(request_builder.return_type, returns.ReturnType)
    assert callable(request_builder.return_type)
    assert request_builder.return_type(mock_response) == str(
        mock_response.json()
    )

    # Verify: Returns JSON when type cannot be converted
    request_builder.get_converter.return_value = None
    returns_json = returns.json(None, ())
    request_builder.return_type = returns.ReturnType.with_decorator(
        None, returns_json
    )
    returns_json.modify_request(request_builder)
    assert callable(request_builder.return_type)
    assert request_builder.return_type(mock_response) == mock_response.json()


def test_returns_json_builtin_type(request_builder, mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"key": "1"}
    request_builder.get_converter.return_value = None
    returns_json = returns.json(type=int, key="key")
    request_builder.return_type = returns.ReturnType.with_decorator(
        None, returns_json
    )
    returns_json.modify_request(request_builder)
    print(request_builder.return_type)
    assert callable(request_builder.return_type)
    assert request_builder.return_type(mock_response) == 1


class TestReturnsJsonCast(object):
    default_value = {"key": "1"}

    @staticmethod
    def prepare_test(request_builder, mocker, value=default_value, **kwargs):
        mock_response = mocker.Mock()
        mock_response.json.return_value = value
        request_builder.get_converter.return_value = None
        returns_json = returns.json(**kwargs)
        request_builder.return_type = returns.ReturnType.with_decorator(
            None, returns_json
        )
        returns_json.modify_request(request_builder)
        return mock_response

    def test_without_type(self, request_builder, mocker):
        mock_response = self.prepare_test(request_builder, mocker, key="key")
        assert request_builder.return_type(mock_response) == "1"

    def test_with_callable_type(self, request_builder, mocker):
        mock_response = self.prepare_test(
            request_builder,
            mocker,
            type=lambda _: "test",
        )
        assert request_builder.return_type(mock_response) == "test"

    def test_with_builtin_type(self, request_builder, mocker):
        mock_response = self.prepare_test(request_builder, mocker, type=str)
        assert request_builder.return_type(mock_response) == str(
            self.default_value
        )

    def test_with_builtin_type_and_key(self, request_builder, mocker):
        mock_response = self.prepare_test(
            request_builder, mocker, key="key", type=int
        )
        assert request_builder.return_type(mock_response) == 1

    def test_with_not_callable_cast(self, request_builder, mocker):
        mock_response = self.prepare_test(request_builder, mocker, type=1)
        assert request_builder.return_type(mock_response) == self.default_value


def test_returns_JsonStrategy(mocker):
    response = mocker.Mock(spec=["json"])
    response.json.return_value = {"hello": "world"}
    converter = returns.JsonStrategy(lambda x: x, "hello")
    assert converter(response) == "world"

    converter = returns.JsonStrategy(lambda y: y + "!", "hello")
    assert converter(response) == "world!"
