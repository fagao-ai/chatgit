from typing import Any, Dict, List

import ormar

from chatgit.common import StrEnum
from chatgit.models import BaseMeta, BaseModelMixins


class RepoSource(StrEnum):
    GITHUB = "github"


class Repositories(ormar.Model, BaseModelMixins):
    class Meta(BaseMeta):
        tablename = "repositories"

    repo_id: int = ormar.Integer()
    name: str = ormar.String(max_length=200)
    index_url: str = ormar.String(max_length=200)
    api_url: str = ormar.String(max_length=200)
    description: str = ormar.Text(nullable=True)
    language: str = ormar.String(max_length=20, nullable=True)
    has_wiki: bool = ormar.Boolean(default=True)
    topics: List[str] = ormar.JSON(nullable=True)
    forks_count: int = ormar.Integer(default=0)
    license: Dict[str, Any] = ormar.JSON(nullable=True)
    readme_content: str = ormar.Text(nullable=True)
    repo_source: RepoSource = ormar.Enum(enum_class=RepoSource, default=RepoSource.GITHUB)


if __name__ == "__main__":
    a = Repositories(
        repo_id=1,
        name="name",
        index_url="name",
        api_url="name",
        description="name",
        language="name",
        has_wiki=True,
        topics=[],
        license={},
        readme_content="",
    )
    print(a.save())
