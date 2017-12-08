# Local imports
from uplink.clients import interfaces

# Collection of handler functions.
_handlers = []


def handler(func):
    """Registers :py:obj:`func` as a handler."""
    # TODO: support handler prioritization
    _handlers.append(func)


def find_client_in_handler_chain(key):
    # Try handlers
    for func in _handlers:
        client = func(key)
        if isinstance(client, interfaces.HttpClientAdapter):
            return client
