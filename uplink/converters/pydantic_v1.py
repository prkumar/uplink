"""
This module defines a converter that uses :py:mod:`pydantic.v1` models
to deserialize and serialize values.
"""

from uplink.converters import register_default_converter_factory
from uplink.converters.interfaces import Factory, Converter
from uplink.utils import is_subclass


def _encode_pydantic_v1(obj):
    from pydantic.v1.json import pydantic_encoder

    # json atoms
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj

    # json containers
    if isinstance(obj, dict):
        return {_encode_pydantic_v1(k): _encode_pydantic_v1(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_encode_pydantic_v1(i) for i in obj]

    # pydantic v1 types
    return _encode_pydantic_v1(pydantic_encoder(obj))


class _PydanticV1RequestBody(Converter):
    def __init__(self, model):
        self._model = model

    def convert(self, value):
        if isinstance(value, self._model):
            return _encode_pydantic_v1(value)
        return _encode_pydantic_v1(self._model.parse_obj(value))


class _PydanticV1ResponseBody(Converter):
    def __init__(self, model):
        self._model = model

    def convert(self, response):
        try:
            data = response.json()
        except AttributeError:
            data = response

        return self._model.parse_obj(data)


class PydanticV1Converter(Factory):
    """
    A converter that serializes and deserializes values using
    :py:mod:`pydantic.v1` models.

    To deserialize JSON responses into Python objects with this
    converter, define a :py:class:`pydantic.v1.BaseModel` subclass and set
    it as the return annotation of a consumer method:

    .. code-block:: python

        @returns.json()
        @get("/users")
        def get_users(self, username) -> List[UserModel]:
            '''Fetch multiple users'''

    Note:

        This converter is an optional feature and requires the
        :py:mod:`pydantic` package. For example, here's how to
        install this feature using pip::

            $ pip install uplink[pydantic]
    """

    try:
        import pydantic_v1 as pydantic_v1
    except ImportError:  # pragma: no cover
        pydantic_v1 = None

    def __init__(self):
        """
        Validates if :py:mod:`pydantic` is installed
        """
        if self.pydantic_v1 is None:
            raise ImportError("No module named 'pydantic'")

    def _get_model(self, type_):
        if is_subclass(type_, self.pydantic_v1.BaseModel):
            return type_
        raise ValueError("Expected pydantic.BaseModel subclass or instance")

    def _make_converter(self, converter, type_):
        try:
            model = self._get_model(type_)
        except ValueError:
            return None

        return converter(model)

    def create_request_body_converter(self, type_, *args, **kwargs):
        return self._make_converter(_PydanticV1RequestBody, type_)

    def create_response_body_converter(self, type_, *args, **kwargs):
        return self._make_converter(_PydanticV1ResponseBody, type_)

    @classmethod
    def register_if_necessary(cls, register_func):
        if cls.pydantic_v1 is not None:
            register_func(cls)


PydanticV1Converter.register_if_necessary(register_default_converter_factory)
