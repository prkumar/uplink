"""
This package defines an adapter layer for handling requests built by
Uplink's high-level, declarative API with existing HTTP clients
(`requests`, `asyncio`, etc.).

We refer to this layer as the backend, as these adapters handle the
actual client behavior (i.e., making a request to a server).

Note:
    At some point, we may want to expose this layer to the user, so
    they can create custom adapters.
"""
# Local imports
from uplink.clients.register import get_client
from uplink.clients.requests_ import RequestsClient
from uplink.clients.twisted_ import TwistedClient

try:
    from uplink.clients.aiohttp_ import AiohttpClient
except (SyntaxError, ImportError) as error:  # pragma: no cover
    from uplink.clients import interfaces

    class AiohttpClient(interfaces.HttpClientAdapter):
        error_message = str(error)

        def __init__(self, *args, **kwargs):
            pass

        def create_request(self):
            raise NotImplementedError(
                "Failed to load `asyncio` client: %s" % self.error_message
            )

__all__ = [
    "RequestsClient",
    "AiohttpClient",
    "TwistedClient",
]

register.set_default_client(RequestsClient)
