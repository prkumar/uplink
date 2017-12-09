import uplink

# Local imports
import github

BASE_URL = "https://api.github.com/"

if __name__ == "__main__":
    # Create a client that uses the marshmallow converter
    gh = github.GitHub(
        base_url=BASE_URL,
        converter=uplink.MarshmallowConverter()
    )

    # Get all public repositories
    repos = gh.get_repos()

    # Shorten to first 10 results to avoid hitting the rate limit.
    repos = repos[:10]

    # Print contributors for those repositories
    for repo in repos:
        contributors = gh.get_contributors(repo.owner, repo.name)
        print("Contributors for %s: %s" % (repo, contributors))
