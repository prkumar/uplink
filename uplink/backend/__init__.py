"""
This package defines an adapter for consuming requests built
by Uplink's high-level, declarative API with existing HTTP clients
(`requests`, `asyncio`, etc.).

We refer to this layer as the backend, as these adapters handle the
actual client behavior (i.e., making a request to a server), and
thus, we refer to this layer as the backend.

Note:
    At some point, we may want to expose this layer to the user, so
    they can create custom adapters.
"""

from uplink.backend.requests_ import RequestsClient

try:
    from uplink.backend.asyncio_ import AsyncioClient
except (SyntaxError, ImportError) as error:
    from uplink.backend import interfaces

    class AsyncioClient(interfaces.HttpClientAdapter):
        error_message = str(error)

        def is_synchronous(self):
            return False

        def __init__(self, *args, **kwargs):
            pass

        def create_request(self):
            raise NotImplementedError(
                "Failed to load `asyncio` client: %s" % self.error_message
            )


DEFAULT_BACKEND = interfaces.Backend(
    RequestsClient(),
    AsyncioClient()
)
