"""
Example of using Uplink with aiohttp for non-blocking HTTP requests.
This should work on Python 3.5 and above.

To support Python 3.4, change ``async def`` to ``def``, replace ``await``
with ``yield from``, and decorate ``get_repo`` with ``asyncio.coroutine``.
"""
import asyncio
import aiohttp
import uplink

# Local imports
from github import BASE_URL, GitHub


async def get_contributors(full_name):
    print('Getting GitHub repository `{}`'.format(full_name))
    response = await gh_async.get_contributors(*full_name.split("/"))
    json = await response.json()
    print('response for {}: {}'.format(full_name, json))
    return json

if __name__ == "__main__":
    # This consumer instance uses Requests to make blocking requests.
    gh_sync = GitHub(base_url=BASE_URL)

    # This uses an aiohttp, an HTTP client for asyncio.
    connector = aiohttp.TCPConnector(verify_ssl=False)
    session = aiohttp.ClientSession(connector=connector)
    client = uplink.AiohttpClient(session)
    gh_async = GitHub(base_url=BASE_URL, client=client)

    # First, let's fetch a list of all public repositories.
    repos = gh_sync.get_repos().json()

    # Use only the first 10 results to avoid hitting the rate limit.
    repos = repos[:10]

    # Concurrently fetch the contributors for those repositories.
    futures = [get_contributors(repo["full_name"]) for repo in repos]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(futures))