import os
from pathlib import Path

from chatgit.common.base_setting import MyBaseSettings

PROJECT_PATH = Path(__file__).absolute().parent.parent.parent

CRAWL_DATA = PROJECT_PATH / "crawl_data"

if not CRAWL_DATA.exists():
    CRAWL_DATA.mkdir()


class Database(MyBaseSettings):
    host: str
    port: int
    username: str
    password: str


class QdrantConnection(MyBaseSettings):
    url: str = None
    host: str = None
    port: int = None
    memory: bool = False


class Config(MyBaseSettings):
    database: Database = Database()
    qdrant: QdrantConnection = QdrantConnection()

    class Config:
        env_file = PROJECT_PATH / "chatgit/config/config.dev.toml"


CONFIG_DIR = PROJECT_PATH / "chatgit/config"

if os.environ.get("ENV") == "dev":
    Config.Config.env_file = CONFIG_DIR / "config.dev.toml"
elif os.environ.get("ENV") == "prod":
    Config.Config.env_file = CONFIG_DIR / "config.prod.toml"

config = Config()
