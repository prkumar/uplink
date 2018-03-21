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


class ListConverter(BaseTypeConverter, interfaces.Converter):

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


class DictConverter(BaseTypeConverter, interfaces.Converter):

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


class _TypeProxy(object):
    def __init__(self, func):
        self._func = func

    def __getitem__(self, item):
        items = item if isinstance(item, tuple) else (item,)
        return self._func(*items)


def _get_types(try_typing=True):
    if TypingConverter.typing and try_typing:
        return TypingConverter.typing.List, TypingConverter.typing.Dict
    else:
        return (
            _TypeProxy(ListConverter.freeze),
            _TypeProxy(DictConverter.freeze)
        )


@register.register_default_converter_factory
class TypingConverter(interfaces.ConverterFactory):
    """
    An adapter that serializes and deserializes collection types defined
    in the :py:mod:`typing` module, such as :py:class:`typing.List`.
    (See :pep:`484` for the specification of type hints in Python.)

    Inner types of a collection are recursively resolved, using other
    available converters if necessary. For instance, when resolving the
    type hint :py:attr:`typing.Sequence[UserSchema]`, where
    :py:attr:`UserSchema` is a custom py:class:`marshmallow.Schema`
    subclass, the converter will resolve the inner type using
    :py:class:`uplink.converters.MarshmallowConverter`.

    TODO: Address how to leverage this converter in Python 3.5 and below.
    """
    try:
        import typing
    except ImportError:  # pragma: no cover
        typing = None

    def _check_typing(self, t):
        return self.typing and inspect.isclass(t) and hasattr(t, "__args__")

    def _base_converter(self, type_):
        if isinstance(type_, BaseTypeConverter.Builder):
            return type_.build()
        elif self._check_typing(type_):
            if issubclass(type_, self.typing.Sequence):
                return ListConverter(*type_.__args__)
            elif issubclass(type_, self.typing.Mapping):
                return DictConverter(*type_.__args__)

    def make_response_body_converter(self, type_, *args, **kwargs):
        return self._base_converter(type_)

    def make_request_body_converter(self, type_, *args, **kwargs):
        return self._base_converter(type_)


TypingConverter.List, TypingConverter.Dict = _get_types()
