# Standard library imports
import collections
import functools
import inspect

# Local imports
from uplink.converters import interfaces, register

__all__ = ["TypingConverter", "ListConverter", "DictConverter"]


class BaseTypeConverter(object):
    Builder = collections.namedtuple("Builder", "build")

    @classmethod
    def freeze(cls, *args, **kwargs):
        return cls.Builder(functools.partial(cls, *args, **kwargs))


class ListConverter(BaseTypeConverter, interfaces.Converter,
                    interfaces.RequiresChain):

    def __init__(self, elem_type):
        self._elem_type = elem_type
        self._elem_converter = None

    def set_chain(self, chain):
        self._elem_converter = chain(self._elem_type)

    def convert(self, value):
        if isinstance(value, (list, tuple)):
            return list(map(self._elem_converter, value))
        else:
            return self._elem_converter(value)


class DictConverter(BaseTypeConverter, interfaces.Converter,
                    interfaces.RequiresChain):

    def __init__(self, key_type, value_type):
        self._key_type = key_type
        self._value_type = value_type
        self._key_converter = None
        self._value_converter = None

    def set_chain(self, chain):
        self._key_converter = chain(self._key_type)
        self._value_converter = chain(self._value_type)

    def convert(self, value):
        if isinstance(value, collections.Mapping):
            key_c, val_c = self._key_converter, self._value_converter
            return dict((key_c(k), val_c(value[k])) for k in value)
        else:
            return self._value_converter(value)


@register.register_converter_factory
class TypingConverter(interfaces.ConverterFactory):
    try:
        import typing
    except ImportError:
        typing = None

    @staticmethod
    def is_subclass(t, ot):
        return inspect.isclass(t) and issubclass(t, ot)

    def _base_converter(self, type_, *args, **kwargs):
        if isinstance(type_, BaseTypeConverter.Builder):
            return type_.build()
        elif self.typing is not None:
            if self.is_subclass(type_, self.typing.List):
                return ListConverter(*type_.__args__)
            elif self.is_subclass(type_, self.typing.Dict):
                return DictConverter(*type_.__args__)

    def make_response_body_converter(self, *args, **kwargs):
        return self._base_converter(*args, **kwargs)

    def make_request_body_converter(self, *args, **kwargs):
        return self._base_converter(*args, **kwargs)
