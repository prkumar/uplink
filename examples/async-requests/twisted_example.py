"""
Example of using Uplink with Twisted for non-blocking HTTP requests.
This should work on Python 2.7 and 3.3+.
"""

# Local imports
from github import BASE_URL, GitHub
from twisted.internet import defer, reactor

import uplink


@defer.inlineCallbacks
def get_contributors(full_name):
    print(f"Getting GitHub repository `{full_name}`")
    response = yield gh_async.get_contributors(*full_name.split("/"))
    json = response.json()
    print(f"response for {full_name}: {json}")


if __name__ == "__main__":
    # This consumer instance uses Requests to make blocking requests.
    gh_sync = GitHub(base_url=BASE_URL)

    # This uses Twisted with Requests, inspired by `requests-threads`.
    gh_async = GitHub(base_url=BASE_URL, client=uplink.TwistedClient())

    # First, let's fetch a list of all public repositories.
    repos = gh_sync.get_repos().json()

    # Use only the first 10 results to avoid hitting the rate limit.
    repos = repos[:10]

    # Asynchronously fetch the contributors for those 10 repositories.
    deferred = [get_contributors(repo["full_name"]) for repo in repos]
    reactor.callLater(2, reactor.stop)  # Stop the reactor after 2 secs
    reactor.run()
