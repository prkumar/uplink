import uplink

# Constants
BASE_URL = "https://api.github.com/"


@uplink.headers({"Accept": "application/vnd.github.v3.full+json"})
class GitHub(uplink.Consumer):

    @uplink.get("/repositories")
    def get_repos(self):
        """Gets all public repositories."""

    @uplink.get("/repos/{owner}/{repo}/contributors")
    def get_contributors(self, owner, repo):
        """Lists contributors for the specified repository."""
