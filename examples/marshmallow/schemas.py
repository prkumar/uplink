import collections
import marshmallow

# == Models == #
Contributor = collections.namedtuple(
    "Contributor", field_names=["username", "contributions"]
)

Repo = collections.namedtuple("Repo", field_names=["owner", "name"])


# == Schemas == #
class ContributorSchema(marshmallow.Schema):
    login = marshmallow.fields.Str(attribute="username")
    contributions = marshmallow.fields.Int()

    @marshmallow.post_load
    def make_contributor(self, data):
        return Contributor(**data)


class RepoSchema(marshmallow.Schema):
    full_name = marshmallow.fields.Str()

    @marshmallow.post_load
    def make_repo(self, data):
        return Repo(*data["full_name"].split("/"))
