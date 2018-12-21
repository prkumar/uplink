from uplink.clients.io.interfaces import (
    Client,
    Executable,
    ExecutionStrategy,
    RequestTemplate,
)
from uplink.clients.io.context import BasicExecutionContext
from uplink.clients.io.templates import CompositeRequestTemplate
from uplink.clients.io.blocking_strategy import BlockingStrategy
from uplink.clients.io.asyncio_strategy import AsyncioStrategy
from uplink.clients.io.twisted_strategy import TwistedStrategy

__all__ = [
    "Client",
    "CompositeRequestTemplate",
    "Executable",
    "ExecutionStrategy",
    "RequestTemplate",
    "BlockingStrategy",
    "AsyncioStrategy",
    "TwistedStrategy",
    "execute",
]


def execute(client, execution, template, request):
    context_ = BasicExecutionContext(client, execution, template, request)
    return execution.execute(context_)
