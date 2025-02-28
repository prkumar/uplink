"""
Example of using Uplink with aiohttp for non-blocking HTTP requests.
This should work on Python 3.7 and above.
"""

import asyncio

# Local imports
from github import BASE_URL, GitHub

import uplink


async def get_contributors(full_name):
    print(f"Getting GitHub repository `{full_name}`")
    response = await gh_async.get_contributors(*full_name.split("/"))
    json = await response.json()
    print(f"response for {full_name}: {json}")
    return json


if __name__ == "__main__":
    # This consumer instance uses Requests to make blocking requests.
    gh_sync = GitHub(base_url=BASE_URL)

    # This uses aiohttp, an HTTP client for asyncio.
    gh_async = GitHub(base_url=BASE_URL, client=uplink.AiohttpClient())

    # First, let's fetch a list of all public repositories.
    repos = gh_sync.get_repos().json()

    # Use only the first 10 results to avoid hitting the rate limit.
    repos = repos[:10]

    # Concurrently fetch the contributors for those repositories.
    futures = [get_contributors(repo["full_name"]) for repo in repos]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*futures))
