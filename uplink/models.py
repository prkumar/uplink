"""
These methods and classes can be used one of two ways. First is as
function decorators:

.. code-block:: python

    # Registers the function as a loader for the given model class.
    @loads.from_json(Model)
    def load_model_from_json(model_type, json):
        ...

With this usage, the decorated function is registered as a default
converter (specifically for the class :py:class:`Model` and its
subclasses).

The alternative usage is to build a converter instance:

    def load_model_from_json(model_type, json):
        ...

    # Creates a converter using the given loader function.
    converter = loads.from_json(Model).using(load_model_from_json)

Unlike the decorator usage, this approach does not register the function
as a default converter, meaning, to use the converter, you must supply
the generated converter object when instantiating a :py:class:`Consumer`
subclass, through the :py:attr:`converter` constructor parameter.

Notably, invoking the :py:meth:`~loads.by_default` method registers the
generated converter object as a default converter, achieving parity
between the two usages. Hence, the follow snippet is equivalent to the
first example using the decorator approach:

.. code-block:: python

    # Registers the function as a loader for the given model class.
    loads.from_json(Model).using(load_model_from_json).by_default()
"""

# Standard library imports
import functools

# Local imports
from uplink import converters, decorators, returns, utils

__all__ = ["loads", "dumps"]

_get_classes = functools.partial(map, type)


class _ModelConverterBuilder(object):

    def __init__(self, base_class, annotations=()):
        """
        Args:
            base_class (type): The base model class.
        """
        self._model_class = base_class
        self._annotations = set(annotations)
        self._func = None

    def using(self, func):
        """Sets the converter strategy to the given function."""
        self._func = func
        return self

    def by_default(self, _r=converters.register_default_converter_factory):
        """Registers this converter as a default converter."""
        _r(self)
        return self

    def __call__(self, func, _r=converters.register_default_converter_factory):
        """
        Sets the converter strategy to the given function and registers
        the converter as a default converter.
        """
        self.using(func).by_default(_r)
        return func

    def _contains_annotations(self, argument_annotations, method_annotations):
        types = set(_get_classes(argument_annotations))
        types.update(_get_classes(method_annotations))
        return types.issuperset(self._annotations)

    def _is_relevant(self, type_, argument_annotations, method_annotations):
        return (
            utils.is_subclass(type_, self._model_class) and
            self._contains_annotations(argument_annotations, method_annotations)
        )

    def _marshall(self, type_, *args, **kwargs):
        if self._is_relevant(type_, *args, **kwargs):
            return functools.partial(self._func, type_)

    @classmethod
    def _make_builder(cls, base_class, annotations, *more_annotations):
        annotations = set(annotations)
        annotations.update(more_annotations)
        return cls(base_class=base_class, annotations=annotations)


# noinspection PyPep8Naming
class loads(_ModelConverterBuilder, converters.ConverterFactory):
    """
    Builds a custom object deserializer.

    This class takes a single argument, the base model class, and
    registers the decorated function as a deserializer for that base
    class and all subclasses.

    Further, the decorated function should accept two positional
    arguments: (1) the encountered type (which can be the given base
    class or a subclass), and (2) the response data.

    .. code-block:: python

        @loads(ModelBase)
        def load_model(model_cls, data):
            ...

    .. versionadded:: v0.5.0
    """

    def make_response_body_converter(self, *args, **kwargs):
        return self._marshall(*args, **kwargs)

    @classmethod
    def from_json(cls, base_class, annotations=()):
        """
        Builds a custom JSON deserialization strategy.

        This decorator accepts the same arguments and behaves like
        :py:class:`uplink.loads`, except that the second argument of the
        decorated function is a JSON object:

        .. code-block:: python

            @loads.from_json(ModelBase)
            def from_json(model_cls, json_object):
                return model_cls.from_json(json_object)

        Notably, only consumer methods that have the expected return type
        (i.e., the given base class or any subclass) and are decorated with
        :py:class:`uplink.returns.json` can leverage the registered strategy
        to deserialize JSON responses.

        For example, the following consumer method would leverage the
        :py:func:`from_json` strategy defined above, given
        :py:class:`User` is a subclass of :py:class:`ModelBase`:

        .. code-block:: python

            @returns.json
            @get("user")
            def get_user(self) -> User: pass

        .. versionadded:: v0.5.0
        """
        return cls._make_builder(base_class, annotations, returns.json)


# noinspection PyPep8Naming
class dumps(_ModelConverterBuilder, converters.ConverterFactory):
    """
    Builds a custom object serializer.

    This decorator takes a single argument, the base model class, and
    registers the decorated function as a serializer for that base
    class and all subclasses.

    Further, the decorated function should accept two positional
    arguments: (1) the encountered type (which can be the given base
    class or a subclass), and (2) the encountered instance.

    .. code-block:: python

        @dumps(ModelBase)
        def deserialize_model(model_cls, model_instance):
            ...

    .. versionadded:: v0.5.0
    """

    def make_request_body_converter(self, *args, **kwargs):
        return self._marshall(*args, **kwargs)

    @classmethod
    def to_json(cls, base_class, annotations=()):
        """
        Builds a custom JSON serialization strategy.

        This decorator accepts the same arguments and behaves like
        :py:class:`uplink.dumps`. The only distinction is that the
        decorated function should be JSON serializable.

        .. code-block:: python

            @dumps.to_json(ModelBase)
            def to_json(model_cls, model_instance):
                return model_instance.to_json()

        Notably, only consumer methods that are decorated with
        py:class:`uplink.json` and have one or more argument annotations
        with the expected type (i.e., the given base class or a subclass)
        can leverage the registered strategy.

        For example, the following consumer method would leverage the
        :py:func:`to_json` strategy defined above, given
        :py:class:`User` is a subclass of :py:class:`ModelBase`:

        .. code-block:: python

            @json
            @post("user")
            def change_user_name(self, name: Field(type=User): pass

        .. versionadded:: v0.5.0
        """
        return cls._make_builder(base_class, annotations, decorators.json)
