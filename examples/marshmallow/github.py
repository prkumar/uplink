import uplink

# Local imports
import schemas


@uplink.headers({"Accept": "application/vnd.github.v3.full+json"})
class GitHub(uplink.Consumer):
    @uplink.returns(schemas.RepoSchema(many=True))
    @uplink.get("/repositories")
    def get_repos(self):
        """Gets all public repositories."""

    @uplink.returns(schemas.ContributorSchema(many=True))
    @uplink.get("/repos/{owner}/{repo}/contributors")
    def get_contributors(self, owner, repo):
        """Lists contributors for the specified repository."""
