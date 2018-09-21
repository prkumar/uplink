import collections
import marshmallow

# == Models == #
Contributor = collections.namedtuple(
    "Contributor", field_names=["username", "contributions"]
)

Repo = collections.namedtuple("Repo", field_names=["owner", "name"])


class SchemaBase(marshmallow.Schema):
    class Meta:
        # Pass EXCLUDE as Meta option to keep marshmallow 2 behavior
        # ref: https://marshmallow.readthedocs.io/en/3.0/upgrading.html
        unknown = getattr(marshmallow, "EXCLUDE", None)


# == Schemas == #
class ContributorSchema(SchemaBase):
    login = marshmallow.fields.Str(attribute="username")
    contributions = marshmallow.fields.Int()

    @marshmallow.post_load
    def make_contributor(self, data):
        return Contributor(**data)


class RepoSchema(SchemaBase):
    full_name = marshmallow.fields.Str()

    @marshmallow.post_load
    def make_repo(self, data):
        return Repo(*data["full_name"].split("/"))
