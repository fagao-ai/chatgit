import ormar

from chatgit.models import BaseMeta, OrmarBaseModel


class Repositories(OrmarBaseModel):
    class Meta(BaseMeta):
        tablename = "repositories"

    repo_id = ormar.Integer()
    name = ormar.String(max_length=200)
    index_url = ormar.String(max_length=200)
    api_url = ormar.String(max_length=200)
    description = ormar.Text()
    language = ormar.String(max_length=20)
    has_wiki = ormar.Boolean(default=True)
    topics = ormar.JSON()
    readme_content = ormar.Text()
