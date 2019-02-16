# Standard library imports
import sys

# Third-party import
import pytest

requires_python34 = pytest.mark.skipif(
    sys.version_info < (3, 4), reason="Requires Python 3.4 or above."
)
