from typing import Any, Dict, Self

import ormar

from chatgit.common import StrEnum
from chatgit.models import BaseModel, database, base_ormar_config


class RepoSource(StrEnum):
    GITHUB = "github"


class Organization(BaseModel):
    ormar_config = base_ormar_config.copy(tablename="organization")  # type: ignore

    org_id: int = ormar.Integer()
    name: str = ormar.String(max_length=200)
    meta: dict[str, Any] = ormar.JSON()


class Repository(BaseModel):
    ormar_config = base_ormar_config.copy(tablename="repository")  # type: ignore

    repo_id: int = ormar.Integer()
    name: str = ormar.String(max_length=200)
    full_name: str = ormar.String(max_length=200)
    organization: Organization | None = ormar.ForeignKey(
        Organization, name="organization_id", nullable=True
    )
    # index_url: str = ormar.String(max_length=200)
    # api_url: str = ormar.String(max_length=200)
    homepage: str | None = ormar.String(max_length=200, nullable=True)
    description: str | None = ormar.Text(nullable=True)
    language: str | None = ormar.String(max_length=20, nullable=True)
    has_wiki: bool = ormar.Boolean(default=True)
    forks_count: int = ormar.Integer(default=0)
    stargazers_count: int = ormar.Integer(default=0)
    license: Dict[str, Any] = ormar.JSON(nullable=True)
    readme_content: str | None = ormar.Text(nullable=True)
    # readme_name: str = ormar.String(max_length=200)
    meta: dict[str, Any] = ormar.JSON()
    repo_source: RepoSource = ormar.Enum(
        enum_class=RepoSource, default=RepoSource.GITHUB
    )

    @classmethod
    @database.transaction()
    async def from_github(
        cls,
        repo_info: dict[str, Any],
        readme: str | None = None,
    ) -> Self:
        if org := repo_info.get("organization"):
            org, _ = await Organization.objects.get_or_create(
                org_id=org["id"], _defaults={"name": org["login"], "meta": org}
            )

        repo, created = await cls.objects.get_or_create(
            repo_id=repo_info["id"],
            _defaults={
                "name": repo_info["name"],
                "full_name": repo_info["full_name"],
                "description": repo_info["description"],
                "language": repo_info.get("language"),
                "has_wiki": repo_info["has_wiki"],
                "forks_count": repo_info["forks_count"],
                "license": repo_info.get("license"),
                "readme_content": readme,
                "homepage": repo_info.get("homepage"),
                "meta": repo_info,
                "organization": org,
                "stargazers_count": repo_info["stargazers_count"],
            },
        )
        if not created:
            return repo

        if topics := repo_info.get("topics"):
            await Topic.objects.bulk_create(
                [Topic(repo=repo, name=topic) for topic in topics]
            )

        return repo


class Topic(BaseModel):
    ormar_config = base_ormar_config.copy(tablename="topic")  # type: ignore

    repo: Repository = ormar.ForeignKey(Repository, name="repo_id")
    name: str = ormar.String(max_length=200, nullable=False)


if __name__ == "__main__":
    import asyncio

    org = Organization(org_id=1, name="sube", meta={"test": "test"})
    asyncio.new_event_loop().run_until_complete(org.save())
