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


class ResponseBodyConverter(interfaces.Converter):
    def convert(self, response):
        return response


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
    def make_response_body_converter(self, type_, *args, **kwargs):
        return ResponseBodyConverter()  # pragma: no cover

    def make_request_body_converter(self, type_, *args, **kwargs):
        return Cast(type_, RequestBodyConverter())  # pragma: no cover

    def make_string_converter(self, type_, *args, **kwargs):
        return Cast(type_, StringConverter())  # pragma: no cover


class ConverterFactoryRegistry(collections.Mapping):
    _converter_factory_registry = {}

    def __init__(self, factories, *args, **kwargs):
        self._factories = tuple(factories)
        self._args = args
        self._kwargs = kwargs

    @property
    def factories(self):
        return iter(self._factories)

    def _make_converter_finder(self, func):
        def wrapper(*args, **kwargs):
            for factory in self.factories:
                converter = func(factory)(*args, **kwargs)
                if converter is not None:
                    return converter
        return functools.partial(wrapper, *self._args, **self._kwargs)

    def _get_converter_factory(self, converter_key):
        return self._make_converter_finder(
            self._converter_factory_registry[converter_key]
        )

    def __getitem__(self, converter_key):
        if callable(converter_key):
            return converter_key(self)
        else:
            return self._get_converter_factory(converter_key)

    def __len__(self):
        return len(self._converter_factory_registry)

    def __iter__(self):
        return iter(self._converter_factory_registry)

    @classmethod
    def register(cls, converter_key):
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
