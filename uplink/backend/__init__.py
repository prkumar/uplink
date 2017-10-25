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

from uplink.backend.requests_ import RequestsBackend

try:
    from uplink.backend.asyncio_ import AsyncioBackend
except (SyntaxError, ImportError) as error:
    from uplink.backend import interfaces

    class AsyncioBackend(interfaces.Backend):
        error_message = str(error)

        def __init__(self, *args, **kwargs):
            pass

        def send_request(self, request):
            raise NotImplementedError(
                "Failed to load `asyncio` client: %s" % self.error_message
            )

