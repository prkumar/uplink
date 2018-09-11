# Standard library imports
import json

# Local imports
from uplink.converters import interfaces, register_default_converter_factory


class Cast(interfaces.Converter):
    def __init__(self, caster, converter):
        self._cast = caster
        self._converter = converter

    def set_chain(self, chain):
        self._converter.set_chain(chain)

    def convert(self, value):
        if callable(self._cast):
            value = self._cast(value)
        return self._converter(value)


class RequestBodyConverter(interfaces.Converter):
    @staticmethod
    def _default_json_dumper(obj):
        return obj.__dict__  # pragma: no cover

    def convert(self, value):
        if isinstance(value, str):
            return value
        dumped = json.dumps(value, default=self._default_json_dumper)
        return json.loads(dumped)


class StringConverter(interfaces.Converter):
    def convert(self, value):
        return str(value)


@register_default_converter_factory
class StandardConverter(interfaces.Factory):
    """
    The default converter, this class seeks to provide sane alternatives
    for (de)serialization when all else fails -- e.g., no other
    converters could handle a particular type.
    """

    def create_response_body_converter(self, type_, *args, **kwargs):
        if isinstance(type_, interfaces.Converter):
            return type_

    def create_request_body_converter(self, type_, *args, **kwargs):
        return Cast(type_, RequestBodyConverter())  # pragma: no cover

    def create_string_converter(self, type_, *args, **kwargs):
        return Cast(type_, StringConverter())  # pragma: no cover
