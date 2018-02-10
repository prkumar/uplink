# Standard library imports
import collections
import functools
import json

# Local imports
from uplink.converters import interfaces, keys
from uplink.converters.marshmallow_ import MarshmallowConverter

__all__ = ["StandardConverter", "MarshmallowConverter"]


class Cast(interfaces.Converter):
    def __init__(self, caster, converter):
        self._cast = caster
        self._converter = converter

    def convert(self, value):
        if callable(self._cast):
            value = self._cast(value)
        return self._converter.convert(value)


class RequestBodyConverter(interfaces.Converter):
    def convert(self, value):
        if isinstance(value, str):
            return value
        else:
            return json.loads(
                json.dumps(value, default=lambda obj: obj.__dict__)
            )


class StringConverter(interfaces.Converter):
    def convert(self, value):
        return str(value)


class StandardConverter(interfaces.ConverterFactory):
    """
    The default converter, this class seeks to provide sane alternatives
    for (de)serialization when all else fails -- e.g., no other
    converters could handle a particular type.
    """

    def make_response_body_converter(self, type_, *args, **kwargs):
        return None  # pragma: no cover

    def make_request_body_converter(self, type_, *args, **kwargs):
        return Cast(type_, RequestBodyConverter())  # pragma: no cover

    def make_string_converter(self, type_, *args, **kwargs):
        return Cast(type_, StringConverter())  # pragma: no cover


class ConverterFactoryRegistry(collections.Mapping):
    """
    A registry that chains together
    :py:class:`interfaces.ConverterFactory` instances.

    When queried for a factory that can handle a particular converter
    type (e.g., ``keys.CONVERT_TO_REQUEST_BODY``), the registry
    traverses the chain until it finds a converter factory that can
    handle the request (i.e., the type's associated method returns a
    value other than ``None``).

    Here's an example -- it's contrived but effectively details the
    expected pattern of usage::

        # Create a registry with a single factory in its chain.
        registry = ConverterFactoryRegistry((StandardConverter,))

        # Get a callable that returns converters for turning arbitrary
        # objects into strings.
        get_str_converter_for_type = registry[keys.CONVERT_TO_STRING]

        # Traverse the chain to find a converter that can handle
        # converting ints into strings.
        converter = get_str_converter_for_type(int)

    Args:
        factories: An iterable of converter factories. Factories that
            appear earlier in the chain are given the opportunity to
            handle a request before those that appear later.
    """

    #: A mapping of keys to callables. Each callable value accepts a
    #: single argument, a :py:class:`interfaces.ConverterFactory`
    #: subclass, and returns another callable, which should return a
    #: :py:`interfaces.Converter` instance.
    _converter_factory_registry = {}

    def __init__(self, factories, *args, **kwargs):
        self._factories = tuple(factories)
        self._args = args
        self._kwargs = kwargs

    @property
    def factories(self):
        """
        Yields the registry's chain of converter factories, in order.
        """
        return iter(self._factories)

    def _make_chain_for_func(self, func):
        def chain(*args, **kwargs):
            for factory in self.factories:
                converter = func(factory)(*args, **kwargs)
                if converter is not None:
                    return converter
        return functools.partial(chain, *self._args, **self._kwargs)

    def _make_chain_for_key(self, converter_key):
        return self._make_chain_for_func(
            self._converter_factory_registry[converter_key]
        )

    def __getitem__(self, converter_key):
        """
        Retrieves a callable that creates converters for the type
        associated to the given key.

        If the given key is a callable, it will be recursively invoked
        to retrieve the final callable. See :py:class:`keys.Map` for
        an example of such a key. These callable keys should accept a
        single argument, a :py:class:`ConverterFactoryRegistry`.
        """
        if callable(converter_key):
            return converter_key(self)
        else:
            return self._make_chain_for_key(converter_key)

    def __len__(self):
        return len(self._converter_factory_registry)

    def __iter__(self):
        return iter(self._converter_factory_registry)

    @classmethod
    def register(cls, converter_key):
        """
        Returns a decorator that can be used to register a callable for
        the given ``converter_key``.
        """
        def wrapper(func):
            cls._converter_factory_registry[converter_key] = func
            return func
        return wrapper


@ConverterFactoryRegistry.register(keys.CONVERT_TO_REQUEST_BODY)
def make_request_body_converter(factory):
    return factory.make_request_body_converter


@ConverterFactoryRegistry.register(keys.CONVERT_FROM_RESPONSE_BODY)
def make_response_body_converter(factory):
    return factory.make_response_body_converter


@ConverterFactoryRegistry.register(keys.CONVERT_TO_STRING)
def make_string_converter(factory):
    return factory.make_string_converter
