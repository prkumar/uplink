# Third-party imports
import pytest

# Local imports
from uplink import _extras


def test_load_entry_points(mocker):
    # Setup
    func = mocker.stub()
    iter_entry_points = mocker.stub()
    entry_point = mocker.Mock()
    entry_point.name = "plugin-name"
    entry_point.load.return_value = "plugin-value"
    iter_entry_points.return_value = [entry_point]
    entry_points = {"entry-point": func}

    # Run
    _extras.load_entry_points(
        _entry_points=entry_points, _iter_entry_points=iter_entry_points
    )

    # Verify
    func.assert_called_with("plugin-value")


def test_install(mocker):
    # Setup
    func = mocker.stub()
    installers = {list: func}
    obj = []

    # Run: Success
    _extras.install(obj, _installers=installers)

    # Verify
    func.assert_called_with(obj)

    # Run & Verify Failure
    with pytest.raises(TypeError):
        _extras.install(dict(), _installers=installers)
