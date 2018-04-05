# Third party imports
import pytest

# Local imports
from uplink import returns
from uplink.converters import register
from uplink.decorators import json
from uplink.models import loads, dumps


@pytest.mark.parametrize("cls, method", [
    (loads, loads.make_response_body_converter),
    (dumps, dumps.make_request_body_converter)
])
def test_models(cls, method):
    # Setup
    registry = register.Register()

    def func(response): response

    # Verify: Add to register
    obj = cls(object, (object,))
    return_value = obj(func, registry.register_converter_factory)
    assert return_value is func
    assert registry.get_converter_factories() == (obj,)

    # Verify: not relevant
    value = method(obj, None, (), ())
    assert value is None

    # Verify: relevant
    value = method(obj, object, (object(),), ())
    assert callable(value)


@pytest.mark.parametrize("cls, method, decorator", [
    (loads.from_json, loads.make_response_body_converter, returns.json()),
    (dumps.to_json, dumps.make_request_body_converter, json())
])
def test_json_builders(cls, method, decorator):
    # Setup
    obj = cls(object)
    obj.using(lambda x: x)

    # Verify: not relevant
    value = method(obj, object, (), ())
    assert value is None

    # Verify relevant
    value = method(obj, object, (), (decorator,))
    assert callable(value)
