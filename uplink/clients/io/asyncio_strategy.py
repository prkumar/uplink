# Third-party imports
import asyncio

# Local models
from uplink.clients.io import interfaces

__all__ = ["AsyncioStrategy"]


class AsyncioStrategy(interfaces.ExecutionStrategy):
    """A non-blocking execution strategy using asyncio."""

    async def send(self, client, request, callback):
        try:
            response = await client.send(request)
        except Exception as error:
            # TODO: Include traceback
            return await callback.on_failure(error, type(error), None)
        else:
            return await callback.on_success(response)

    async def sleep(self, duration, callback):
        await asyncio.sleep(duration)
        return await callback.on_success()

    async def finish(self, response):
        return response

    async def execute(self, executable):
        return await executable.execute()
