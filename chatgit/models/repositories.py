from typing import Any, Dict

import ormar

from chatgit.models import BaseMeta, OrmarBaseModel
from chatgit.utils.typed import Text


class Repositories(OrmarBaseModel):
    class Meta(BaseMeta):
        tablename = "repositories"

    repo_id: int = ormar.Integer()
    name: str = ormar.String(max_length=200)
    index_url: str = ormar.String(max_length=200)
    api_url: str = ormar.String(max_length=200)
    description: Text = ormar.Text()
    language: str = ormar.String(max_length=20)
    has_wiki: bool = ormar.Boolean(default=True)
    topics: Dict[str, Any] = ormar.JSON()
    readme_content: Text = ormar.Text()
