from uplink.clients.io.interfaces import (
    Client,
    Executable,
    IOStrategy,
    RequestTemplate,
)
from uplink.clients.io.execution import RequestExecutionBuilder
from uplink.clients.io.templates import CompositeRequestTemplate
from uplink.clients.io.blocking_strategy import BlockingStrategy
from uplink.clients.io.twisted_strategy import TwistedStrategy

__all__ = [
    "Client",
    "CompositeRequestTemplate",
    "Executable",
    "IOStrategy",
    "RequestTemplate",
    "BlockingStrategy",
    "AsyncioStrategy",
    "TwistedStrategy",
    "RequestExecutionBuilder",
]

try:
    from uplink.clients.io.asyncio_strategy import AsyncioStrategy
except (ImportError, SyntaxError):  # pragma: no cover

    class AsyncioStrategy(IOStrategy):
        def __init__(self, *args, **kwargs):
            raise NotImplementedError(
                "Failed to load `asyncio` execution strategy: you may be using a version "
                "of Python below 3.3. `aiohttp` requires Python 3.4+."
            )
