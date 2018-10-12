# Local imports
from uplink import returns


def test_returns(request_builder):
    request_builder.get_converter.return_value = str
    custom = returns(str)
    custom.modify_request(request_builder)
    assert request_builder.return_type.unwrap() is str


def test_returns_json(request_builder):
    request_builder.get_converter.return_value = str
    returns_json = returns.json(str, ())
    returns_json.modify_request(request_builder)
    assert isinstance(request_builder.return_type, returns._StrategyWrapper)

    # Verify: Idempotent
    returns_json.modify_request(request_builder)
    assert isinstance(request_builder.return_type, returns._StrategyWrapper)
    assert request_builder.return_type.unwrap() is str

    # Verify: Doesn't apply to unsupported types
    request_builder.get_converter.return_value = None
    request_builder.return_type = None
    returns_json = returns.json(str, ())
    returns_json.modify_request(request_builder)
    assert request_builder.return_type is None


def test_StrategyWrapper():
    wrapper = returns._StrategyWrapper(None, lambda x: x)
    assert wrapper("hello") == "hello"


def test_returns_JsonStrategy(mocker):
    response = mocker.Mock(spec=["json"])
    response.json.return_value = {"hello": "world"}
    converter = returns.JsonStrategy(lambda x: x, "hello")
    assert converter(response) == "world"

    converter = returns.JsonStrategy(lambda y: y + "!", "hello")
    assert converter(response) == "world!"

    assert returns.JsonStrategy(1).unwrap() == 1
