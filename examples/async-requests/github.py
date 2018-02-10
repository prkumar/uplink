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

if __name__ == "__main__":
    # Executes the code above
    # The for loop is used for readability, you can just call print(response.json())

    # Gets all public repositories
    github = GitHub(BASE_URL)
    response = github.get_repos()
    for repos in response.json():
        print(repos)

    # Lists contributors for a repository
    github = GitHub(BASE_URL)
    response = github.get_contributors("prkumar", "uplink")
    for contributors in response.json():
        print(contributors)