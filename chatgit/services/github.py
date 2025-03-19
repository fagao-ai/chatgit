import os
import base64
import re
from typing import Any, ClassVar, Tuple
from httpx import AsyncClient

from chatgit.common.config import DB_ENABLE
from chatgit.models.repositories import Repository


class Github:
    OWNER_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"https?:\/\/github\.com\/([^\/]+)\/([^\/?]+)(?:\.git)?(?:\?.*)?$"
    )

    def __init__(self, url: str = "https://api.github.com", token: str | None = None):
        self.url = url
        self.token = token or os.environ.get("GITHUB_TOKEN")
        assert self.token, "Please set GITHUB_TOKEN in your environment variables"

        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "chatGit",
            "Authorization": f"Bearer {self.token}",
        }

    @classmethod
    def parse_github_url(cls, url: str) -> Tuple[str, str]:
        match = cls.OWNER_PATTERN.search(url)
        if match:
            return match.group(1), match.group(2)
        raise ValueError("Invalid GitHub URL")

    async def get_readme(self, repo_url: str) -> str:
        owner, repo = self.parse_github_url(repo_url)

        async with AsyncClient(base_url=self.url, headers=self.headers) as client:
            response = await client.get(f"/repos/{owner}/{repo}/readme")
            response.raise_for_status()

            content = response.json()["content"]
            content = base64.b64decode(content).decode("utf-8")
            if DB_ENABLE and content:
                repo_info = await self.get_repo_info(repo_url)
                await Repository.from_github(readme=content, repo_info=repo_info)
            return content

    async def get_repo_info(self, repo_url: str) -> dict[str, Any]:
        owner, repo = self.parse_github_url(repo_url)

        async with AsyncClient(base_url=self.url, headers=self.headers) as client:
            response = await client.get(f"/repos/{owner}/{repo}")
            response.raise_for_status()

            return response.json()


if __name__ == "__main__":
    import asyncio

    github = Github(token="")
    readme = asyncio.new_event_loop().run_until_complete(
        github.get_repo_info(
            "https://github.com/vectordotdev/vector?utm_source=gold_browser_extension"
        )
    )
    print(readme)
