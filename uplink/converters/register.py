# Standard library imports
import collections

# Local imports
from uplink.converters import interfaces


class Register(object):

    def __init__(self):
        self._register = collections.deque()

    def register_converter_factory(self, factory_proxy):
        factory = factory_proxy() if callable(factory_proxy) else factory_proxy
        if not isinstance(factory, interfaces.ConverterFactory):
            raise TypeError(
                "Failed to register '%s' as a converter factory: it is not an "
                "instance of '%s'." % (factory, interfaces.ConverterFactory)
            )
        self._register.appendleft(factory)
        return factory_proxy

    def get_converter_factories(self):
        return tuple(self._register)


_registry = Register()

register_converter_factory = _registry.register_converter_factory
get_default_converter_factories = _registry.get_converter_factories

