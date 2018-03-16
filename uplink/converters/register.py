# Standard library imports
import collections

# Local imports
from uplink.converters import interfaces

_default_converter_factories = collections.deque()


def register_converter_factory(factory_proxy):
    factory = factory_proxy() if callable(factory_proxy) else factory_proxy
    if not isinstance(factory, interfaces.ConverterFactory):
        raise TypeError(
            "Failed to register '%s' as converter factory: it is not an "
            "instance of '%s'." % (factory, interfaces.ConverterFactory)
        )
    _default_converter_factories.appendleft(factory)
    return factory_proxy


def get_default_converter_factories():
    return tuple(_default_converter_factories)
