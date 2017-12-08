# Standard library imports
import collections

# Local imports
from uplink import interfaces, utils


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
        self._uri_builder = None
        self._return_type = None
        self._info = collections.defaultdict(dict)
        self._converter_registry = converter_registry

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, method):
        self._method = method

    @property
    def uri(self):
        return self._uri_builder

    @uri.setter
    def uri(self, uri):
        self._uri_builder = utils.URIBuilder(uri)

    @property
    def info(self):
        return self._info

    def get_converter(self, converter_key, *args, **kwargs):
        return self._converter_registry[converter_key](*args, **kwargs)

    def set_return_type(self, return_type):
        self._return_type = return_type

    def build(self):
        # TODO: Should we assert that all URI variables are set?
        # assert not self._uri_builder.remaining_variables():
        return utils.Request(
            self._method,
            self._uri_builder.build(),
            self._info,
            self._return_type
        )
