# Standard library imports
import collections

# Local imports
from uplink import interfaces


def get_api_definitions(service):
    """
    Returns all attributes with type
    `uplink.interfaces.RequestDefinitionBuilder` defined on the given
    class.

    Note:
        Only attributes defined directly on the class are considered. In
        other words, inherited `RequestDefinitionBuilder` attributes
        are ignored.

    Args:
        service: A class object.
    """
    # In Python 3.3, `inspect.getmembers` doesn't respect the descriptor
    # protocol when the first argument is a class. In other words, the
    # function includes any descriptors bound to `service` as is rather
    # than calling the descriptor's __get__ method. This is seemingly
    # fixed in Python 2.7 and 3.4+ (TODO: locate corresponding bug
    # report in Python issue tracker). Directly invoking `getattr` to
    # force Python's attribute lookup protocol is a decent workaround to
    # ensure parity:
    class_attributes = ((k, getattr(service, k)) for k in service.__dict__)

    is_definition = interfaces.RequestDefinitionBuilder.__instancecheck__
    return [(k, v) for k, v in class_attributes if is_definition(v)]


def set_api_definition(service, name, definition):
    setattr(service, name, definition)


class RequestBuilder(object):
    def __init__(self, converter_registry):
        self._method = None
        self._url = None
        self._return_type = None

        # TODO: Pass this in as constructor parameter
        # TODO: Delegate instantiations to uplink.HTTPClientAdapter
        self._info = collections.defaultdict(dict)

        self._converter_registry = converter_registry
        self._transaction_hooks = []

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, method):
        self._method = method

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    @property
    def info(self):
        return self._info

    @property
    def transaction_hooks(self):
        return iter(self._transaction_hooks)

    def get_converter(self, converter_key, *args, **kwargs):
        return self._converter_registry[converter_key](*args, **kwargs)

    @property
    def return_type(self):
        return self._return_type

    @return_type.setter
    def return_type(self, return_type):
        self._return_type = return_type

    def add_transaction_hook(self, hook):
        self._transaction_hooks.append(hook)
