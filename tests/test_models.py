# Third party imports
import pytest

# Local imports
from uplink import returns
from uplink.decorators import json
from uplink.models import loads, dumps


@pytest.mark.parametrize(
    "cls, method",
    [
        (loads, "create_response_body_converter"),
        (dumps, "create_request_body_converter"),
    ],
)
def test_models(mocker, cls, method, request_definition):
    # Setup
    func = mocker.stub()
    func.return_value = 1

    # Verify: Returns obj that wraps func
    obj = cls(object, (object,))
    factory = obj(func)
    assert callable(factory)
    assert factory(1) == 1

    # Verify: not relevant
    request_definition.argument_annotations = ()
    request_definition.method_annotations = ()
    value = getattr(factory, method)(None, request_definition)
    assert value is None

    # Verify: relevant
    request_definition.argument_annotations = (object(),)
    value = getattr(factory, method)(object, request_definition)
    assert callable(value)


@pytest.mark.parametrize(
    "cls, method, decorator",
    [
        (loads.from_json, "create_response_body_converter", returns.json()),
        (dumps.to_json, "create_request_body_converter", json()),
    ],
)
def test_json_builders(mocker, cls, method, decorator, request_definition):
    # Setup
    func = mocker.stub()
    func.return_value = 1
    obj = cls(object)
    factory = obj.using(func)

    # Verify: not relevant
    request_definition.argument_annotations = ()
    request_definition.method_annotations = ()
    value = getattr(factory, method)(object, request_definition)
    assert value is None

    # Verify relevant
    request_definition.method_annotations = (decorator,)
    value = getattr(factory, method)(object, request_definition)
    assert callable(value)
    assert value(1) == 1
