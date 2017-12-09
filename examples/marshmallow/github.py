from uplink import Consumer, get, headers

# Local imports
from schemas import RepoSchema, ContributorSchema


@headers({"Accept": "application/vnd.github.v3.full+json"})
class GitHub(Consumer):
    @get("/repositories")
    def get_repos(self) -> RepoSchema(many=True):
        """Lists all public repositories."""

    @get("/repos/{owner}/{repo}/contributors")
    def get_contributors(self, owner, repo) -> ContributorSchema(many=True):
        """Lists contributors for the specified repository."""
