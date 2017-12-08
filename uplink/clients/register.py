# Local imports
from uplink.clients import interfaces

# (default client, handlers)
_registrar = [None, []]


def handler(func):
    """Registers :py:obj:`func` as a handler."""
    # TODO: support handler prioritization?
    _registrar[1].append(func)


def handle_client_key(key):
    # Try handlers
    for func in _registrar[1]:
        client = func(key)
        if isinstance(client, interfaces.HttpClientAdapter):
            return client


def set_default_client(client):
    _registrar[0] = client


def get_default_client():
    default_client = _registrar[0]
    if callable(default_client):
        return default_client()
    else:
        return default_client


def get_client(client):
    if client is None:
        client = get_default_client()

    if isinstance(client, interfaces.HttpClientAdapter):
        return client
    else:
        # Try handlers
        return handle_client_key(client)
