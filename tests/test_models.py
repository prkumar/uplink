# Third party imports
import pytest

# Local imports
from uplink import returns
from uplink.decorators import json
from uplink.models import loads, dumps


@pytest.mark.parametrize("cls, method", [
    (loads, "make_response_body_converter"),
    (dumps, "make_request_body_converter")
])
def test_models(mocker, cls, method):
    # Setup
    func = mocker.stub()
    func.return_value = 1

    # Verify: Returns obj that wraps func
    obj = cls(object, (object,))
    factory = obj(func)
    assert callable(factory)
    assert factory(1) == 1

    # Verify: not relevant
    value = getattr(factory, method)(None, (), ())
    assert value is None

    # Verify: relevant
    value = getattr(factory, method)(object, (object(),), ())
    assert callable(value)


@pytest.mark.parametrize("cls, method, decorator", [
    (loads.from_json, "make_response_body_converter", returns.json()),
    (dumps.to_json, "make_request_body_converter", json())
])
def test_json_builders(mocker, cls, method, decorator):
    # Setup
    func = mocker.stub()
    func.return_value = 1
    obj = cls(object)
    factory = obj.using(func)

    # Verify: not relevant
    value = getattr(factory, method)(object, (), ())
    assert value is None

    # Verify relevant
    value = getattr(factory, method)(object, (), (decorator,))
    assert callable(value)
    assert value(1) == 1
