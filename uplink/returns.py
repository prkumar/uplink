# Standard library imports
import sys

# Local imports
from uplink import decorators
from uplink.converters import keys, interfaces

__all__ = ["from_json", "json", "model"]


class _ReturnsBase(decorators.MethodAnnotation):

    def _get_return_type(self, return_type):  # pragma: no cover
        return return_type

    def _make_strategy(self, converter):  # pragma: no cover
        pass

    def modify_request(self, request_builder):
        return_type = self._get_return_type(request_builder.return_type)
        if isinstance(return_type, _StrategyWrapper):
            converter = return_type.unwrap()
        else:
            converter = request_builder.get_converter(
                keys.CONVERT_FROM_RESPONSE_BODY,
                return_type
            )
        if converter is not None:
            # Found a converter that can handle the return type.
            request_builder.return_type = _StrategyWrapper(
                converter,
                self._make_strategy(converter)
            )


class _StrategyWrapper(object):

    def __init__(self, converter, strategy):
        self._converter = converter
        self._strategy = strategy

    def __call__(self, *args, **kwargs):
        return self._strategy(*args, **kwargs)

    def unwrap(self):  # pragma: no cover
        return self._converter


class JsonStrategy(object):
    # TODO: Consider moving this under json decorator
    # TODO: Support JSON Pointer (https://tools.ietf.org/html/rfc6901)

    def __init__(self, converter, member=()):
        self._converter = converter

        if not isinstance(member, (list, tuple)):
            member = (member,)
        self._member = member

    def __call__(self, response):
        content = response.json()
        for name in self._member:
            content = content[name]
        content = self._converter(content)
        return content

    def unwrap(self):
        return self._converter


# noinspection PyPep8Naming
class json(_ReturnsBase):
    """
    Specifies that the decorated consumer method should return a JSON
    object. If a :py:obj:`model` is provided, the resulting JSON object
    is converted into the :py:obj:`model` object using an appropriate
    converter (see :py:meth:`uplink.loads.from_json`).

    .. code-block:: python

        # This method will return a JSON object (e.g., a dict or list)
        @returns.json
        @get("/users/{username}")
        def get_user(self, username):
            \"""Get a specific user.\"""

    Returning a Specific JSON Field:

        This decorator accepts two optional arguments. The
        :py:attr:`member` argument accepts a string or tuple that
        specifies the path of an internal field in the JSON document.

        For instance, consider an API that returns JSON responses that,
        at the root of the document, contains both the server-retrieved
        data and a list of relevant API errors:

        .. code-block:: json
            :emphasize-lines: 2

            {
                "data": { "user": "prkumar", "id": 140232 },
                "errors": []
            }

        If returning the list of errors is unnecessary, we can use the
        :py:attr:`member` argument to strictly return the inner field
        :py:attr:`data`:

        .. code-block:: python

            @returns.json(member="data")
            @get("/users/{username}")
            def get_user(self, username):
                \"""Get a specific user.\"""

    Deserialize Objects from JSON:

        Often, JSON responses represent models in your application. If
        an existing Python object encapsulates this model, use the
        :py:attr:`model` argument to specify it as the return type:

        .. code-block:: python

            @returns.json(model=User)
            @get("/users/{username}")
            def get_user(self, username):
                \"""Get a specific user.\"""

        For Python 3 users, you can alternatively provide a return value
        annotation. Hence, the previous code is equivalent to the
        following in Python 3:

        .. code-block:: python

            @returns.json
            @get("/users/{username}")
            def get_user(self, username) -> User:
                \"""Get a specific user.\"""

        Both usages typically require also registering a converter that
        knows how to deserialize the JSON into your data model object
        (see :py:meth:`uplink.loads.from_json`). This step is
        unnecessary if these objects are defined using a library for
        whom Uplink has built-in support, such as :py:mod:`marshmallow`
        (see :py:class:`uplink.converters.MarshmallowConverter`).

    .. versionadded:: v0.5.0
    """
    _can_be_static = True

    class _DummyConverter(interfaces.Converter):
        def convert(self, response):
            return response

    __dummy_converter = _DummyConverter()

    def __init__(self, model=None, member=()):
        self._model = model
        self._member = member

    def _get_return_type(self, return_type):
        # If the model and return type are None, the strategy should
        # directly return the JSON body of the HTTP response, instead of
        # trying to deserialize it into a model. In this case, by
        # defaulting the return type to the dummy converter, which
        # implements this pass-through behavior, we ensure that
        # _make_strategy is called.
        default = self.__dummy_converter if self._model is None else self._model

        return default if return_type is None else return_type

    def _make_strategy(self, converter):
        return JsonStrategy(converter, self._member)


from_json = json


# noinspection PyPep8Naming
class model(_ReturnsBase):
    """
    Specifies that the function returns a specific class.

    In Python 3, to provide a consumer method's return type, you can
    set it as the method's return annotation:

    .. code-block:: python

        @get("/users/{username}")
        def get_user(self, username) -> UserSchema:
            \"""Get a specific user.\"""

    For Python 2.7 compatibility, you can use this decorator instead:

    .. code-block:: python

        @returns.model(UserSchema)
        @get("/users/{username}")
        def get_user(self, username):
            \"""Get a specific user.\"""

    To have Uplink convert response bodies into the desired type, you
    will need to define an appropriate converter (e.g., using
    :py:class:`uplink.loads`).

    .. versionadded:: v0.5.1
    """

    def __init__(self, type):
        self._type = type

    def _get_return_type(self, return_type):
        return self._type if return_type is None else return_type

    def _make_strategy(self, converter):
        return converter


class _ModuleProxy(object):
    __module = sys.modules[__name__]

    model = model
    json = json
    from_json = from_json
    __all__ = __module.__all__

    def __getattr__(self, item):
        return getattr(self.__module, item)

    def __call__(self, *args, **kwargs):
        return model(*args, **kwargs)


sys.modules[__name__] = _ModuleProxy()
