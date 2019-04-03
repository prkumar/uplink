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
    ) = returns.ReturnType.with_decorator(
        first_type, decorator2
    )

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

    # Verify: Doesn't apply to unsupported types
    request_builder.get_converter.return_value = None
    returns_json = returns.json(str, ())
    request_builder.return_type = returns.ReturnType.with_decorator(
        None, returns_json
    )
    returns_json.modify_request(request_builder)
    assert not callable(request_builder.return_type)


def test_returns_JsonStrategy(mocker):
    response = mocker.Mock(spec=["json"])
    response.json.return_value = {"hello": "world"}
    converter = returns.JsonStrategy(lambda x: x, "hello")
    assert converter(response) == "world"

    converter = returns.JsonStrategy(lambda y: y + "!", "hello")
    assert converter(response) == "world!"

    assert returns.JsonStrategy(1).unwrap() == 1
