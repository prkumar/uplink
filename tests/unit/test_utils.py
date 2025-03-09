# Standard library imports

# Local imports
from uplink import utils


def test_get_arg_spec():
    def func(pos1, *args: 2, **kwargs: 3) -> 4:
        pass

    signature = utils.get_arg_spec(func)
    assert isinstance(signature, utils.Signature)
    assert signature.args == ["pos1", "args", "kwargs"]
    assert signature.annotations == {"args": 2, "kwargs": 3}
    assert signature.return_annotation == 4


def test_call_args():
    def func(pos1, *args, **kwargs):
        pass

    call_args = utils.get_call_args(func, 1, 2, named=3)
    assert call_args == {"pos1": 1, "args": (2,), "kwargs": {"named": 3}}


class TestURIBuilder:
    def test_variables_not_string(self):
        assert utils.URIBuilder.variables(None) == set()

    def test_set_variable(self):
        builder = utils.URIBuilder("/path/to/{variable}")
        assert builder.build() == "/path/to/"
        builder.set_variable(variable="resource")
        assert builder.build() == "/path/to/resource"

    def test_remaining_variables(self):
        builder = utils.URIBuilder("{variable}")
        assert builder.remaining_variables() == {"variable"}
        builder.set_variable(variable="resource")
        assert len(builder.remaining_variables()) == 0
