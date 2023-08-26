import os
from pathlib import Path

from pydantic.main import BaseModel

from chatgit.common.my_base_settings import MyBaseSettings

PROJECT_PATH = Path(__file__).absolute().parent.parent.parent

CRAWL_DATA = PROJECT_PATH / "crawl_data"

if not CRAWL_DATA.exists():
    CRAWL_DATA.mkdir()


class Database(BaseModel):
    host: str
    port: int
    username: str
    password: str
    db_name: str


class QdrantConnection(BaseModel):
    url: str | None = None
    host: str | None = None
    port: int | None = None
    memory: bool | None = False


class Config(MyBaseSettings):
    database: Database
    qdrant: QdrantConnection = QdrantConnection()

    class Config:
        env_file = PROJECT_PATH / "chatgit/config/config.dev.toml"


CONFIG_DIR = PROJECT_PATH / "chatgit/config"

if os.environ.get("ENV") == "dev":
    Config.Config.env_file = CONFIG_DIR / "config.dev.toml"
elif os.environ.get("ENV") == "prod":
    Config.Config.env_file = CONFIG_DIR / "config.prod.toml"

config = Config()


if __name__ == "__main__":
    print(config)
