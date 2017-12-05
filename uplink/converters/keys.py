# Standard library imports
import functools

# Local imports
from uplink.converters import interfaces

__all__ = [
    "CONVERT_TO_STRING",
    "CONVERT_TO_REQUEST_BODY",
    "CONVERT_FROM_RESPONSE_BODY",
    "Map",
    "Sequence"
]

# Constants
CONVERT_TO_STRING = 0
CONVERT_TO_REQUEST_BODY = 1
CONVERT_FROM_RESPONSE_BODY = 2


class ConverterFunction(interfaces.Converter):
    def __init__(self, convert_function):
        self._convert = convert_function

    def convert(self, value):
        return self._convert(value)


class CompositeKey(object):
    def __init__(self, converter_key):
        self._converter_key = converter_key

    def __eq__(self, other):
        if isinstance(other, CompositeKey) and type(other) is type(self):
            return other._converter_key == self._converter_key
        return False

    def convert(self, converter, value):  # pragma: no cover
        raise NotImplementedError

    def __call__(self, converter_registry):
        factory = converter_registry[self._converter_key]

        def factory_wrapper(*args, **kwargs):
            converter = factory(*args, **kwargs)
            convert_func = functools.partial(self.convert, converter)
            return ConverterFunction(convert_func)

        return factory_wrapper


class Map(CompositeKey):
    def convert(self, converter, value):
        return dict((k, converter.convert(value[k])) for k in value)


class Sequence(CompositeKey):
    def convert(self, converter, value):
        if isinstance(value, (list, tuple)):
            return list(map(converter.convert, value))
        else:
            return converter.convert(value)
