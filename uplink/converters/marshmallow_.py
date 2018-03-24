"""
This module defines a converter that uses :py:mod:`marshmallow` schemas
to deserialize and serialize values.
"""

# Local imports
from uplink import utils
from uplink.converters import interfaces, register


class MarshmallowConverter(interfaces.ConverterFactory):
    """
    A converter that serializes and deserializes values using
    :py:mod:`marshmallow` schemas.

    To deserialize JSON responses into Python objects with this
    converter, define a :py:class:`marshmallow.Schema` subclass and set
    it as the return annotation of a consumer method:

    .. code-block:: python

        @get("/users")
        def get_users(self, username) -> UserSchema():
            '''Fetch a single user'''

    Note:

        This converter is an optional feature and requires the
        :py:mod:`marshmallow` package. For example, here's how to
        install this feature using pip::

            $ pip install uplink[marshmallow]
    """

    try:
        import marshmallow
    except ImportError:  # pragma: no cover
        marshmallow = None

    def __init__(self):
        if self.marshmallow is None:
            raise ImportError("No module named 'marshmallow'")

    class ResponseBodyConverter(interfaces.Converter):

        def __init__(self, schema):
            self._schema = schema

        def convert(self, response):
            try:
                json = response.json()
            except AttributeError:
                # Assume that the response is already json
                json = response

            try:
                return self._schema.load(json).data
            except MarshmallowConverter.marshmallow.exceptions.MarshmallowError:
                return response

    class RequestBodyConverter(interfaces.Converter):
        def __init__(self, schema):
            self._schema = schema

        def convert(self, value):
            return self._schema.dump(value).data

    @classmethod
    def _get_schema(cls, type_):
        if utils.is_subclass(type_, cls.marshmallow.Schema):
            return type_()
        elif isinstance(type_, cls.marshmallow.Schema):
            return type_
        raise ValueError("Expected marshmallow.Scheme subclass or instance.")

    def _make_converter(self, converter_cls, type_):
        try:
            # Try to generate schema instance from the given type.
            schema = self._get_schema(type_)
        except ValueError:
            # Failure: the given type is not a `marshmallow.Schema`.
            return None
        else:
            return converter_cls(schema)

    def make_request_body_converter(self, type_, *args, **kwargs):
        return self._make_converter(self.RequestBodyConverter, type_)

    def make_response_body_converter(self, type_, *args, **kwargs):
        return self._make_converter(self.ResponseBodyConverter, type_)

    @classmethod
    def register_if_necessary(cls, register_func):
        if cls.marshmallow is not None:
            register_func(cls)


MarshmallowConverter.register_if_necessary(
    register.register_default_converter_factory
)
