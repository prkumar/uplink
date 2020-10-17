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

    @staticmethod
    def pass_through_converter(type_, *args, **kwargs):
        return type_

    create_response_body_converter = (
        create_request_body_converter
    ) = pass_through_converter

    def create_string_converter(self, type_, *args, **kwargs):
        return Cast(type_, StringConverter())  # pragma: no cover
