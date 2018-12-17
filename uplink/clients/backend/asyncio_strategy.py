# Third-party imports
import asyncio

# Local models
from uplink.clients.backend import interfaces


class AsyncioStrategy(interfaces.ExecutionStrategy):
    async def send(self, client, request, callback):
        try:
            response = await client.send(request)
        except Exception as error:
            # TODO: Include traceback
            return await callback.on_failure(error, type(error), None)
        else:
            return await callback.on_success(response)

    async def wait(self, duration, callback):
        await asyncio.sleep(duration)
        return await callback.on_success()

    async def finish(self, response):
        return response

    async def execute(self, executable):
        return await executable.execute()
