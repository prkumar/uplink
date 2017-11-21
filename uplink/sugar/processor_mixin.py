import inspect

from functools import wraps

from ..exceptions import Error as UplinkError
from ..builder import CallFactory

class ProcessorMixinError(UplinkError):
    pass


class ProcessorMixin(object):
    ''' A mixin that can be used to extend functionality for subclasses
    of consumers, esp. those who intend to override consumer methods '''

    METHOD_OVERRIDES_ATTR = '__is_processormixin_override'

    def __init__(self, *args, **kwargs):
        super(ProcessorMixin, self).__init__(*args, **kwargs)
        self._perform_checks()

    def _perform_checks(self):
        self._perform_overrides_checks()

    def _perform_overrides_checks(self):
        ''' Check for any functions which are decorated with @overrides to
        see if they actually override anything '''
        methods = inspect.getmembers(self, inspect.ismethod)
        super_class = super(ProcessorMixin, self)

        override_methods = [
            method for method in methods if
            hasattr(method[1], self.METHOD_OVERRIDES_ATTR) and
            getattr(method[1], self.METHOD_OVERRIDES_ATTR) 
        ]

        for method_name, _ in override_methods:
            if not hasattr(super_class, method_name):
                raise ProcessorMixinError(
                    "class {} does not have method {} to override"
                    .format(super_class, method_name)
                )


            super_method = getattr(super_class, method_name)
            if not isinstance(super_method, CallFactory):
                raise ProcessorMixinError(
                    "method {}::{} is not an overridable uplink request"
                    .format(super_class, method_name)
                )


def overrides(func):
    ''' A decorator to assert, upon class creation time, that all override
    functions actually override a proper, existing function, and that they
    are of uplink requestdefintion types '''
    setattr(func, ProcessorMixin.METHOD_OVERRIDES_ATTR, True)
    return func