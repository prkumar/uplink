# Third party imports
import pytest

# Local imports
from uplink import models
from uplink.converters import register


@pytest.mark.parametrize("cls, method", [
    (models.load, models.load.make_response_body_converter),
    (models.dump, models.dump.make_request_body_converter)
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

