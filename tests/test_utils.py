# Standard library imports
import sys

# Local imports
from uplink import utils

is_py2 = sys.version_info[0] == 2


def test_get_arg_spec():
    if is_py2:
        code = "def func(pos1, *args, **kwargs): pass"
    else:
        code = "def func(pos1, *args: 2, **kwargs: 3) -> 4: pass"
    exec(code, globals(), locals())
    signature = utils.get_arg_spec(locals()["func"])
    assert isinstance(signature, utils.Signature)
    assert signature.args == ["pos1", "args", "kwargs"]
    if not is_py2:
        assert signature.annotations == {"args": 2, "kwargs": 3}
        assert signature.return_annotation == 4


def test_call_args():
    def func(pos1, *args, **kwargs):
        pass

    call_args = utils.get_call_args(func, 1, 2, named=3)
    assert call_args == {"pos1": 1, "args": (2,), "kwargs": {"named": 3}}


class TestURIBuilder(object):
    def test_variables_not_string(self):
        assert utils.URIBuilder.variables(None) == set()

    def test_set_variable(self):
        builder = utils.URIBuilder("/path/to/{variable}")
        assert builder.build() == "/path/to/"
        builder.set_variable(variable="resource")
        assert builder.build() == "/path/to/resource"

    def test_remaining_variables(self):
        builder = utils.URIBuilder("{variable}")
        assert builder.remaining_variables() == set(["variable"])
        builder.set_variable(variable="resource")
        assert builder.remaining_variables() == set()
