import os

from pydantic.main import BaseModel

from chatgit.common import PROJECT_PATH
from chatgit.common.my_base_settings import MyBaseSettings


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

ENV = os.getenv("ENV", "prod")

if ENV == "dev":
    Config.Config.env_file = CONFIG_DIR / "config.dev.toml"
elif ENV == "prod":
    Config.Config.env_file = CONFIG_DIR / "config.prod.toml"

config = Config()

db_url = (
    f"mysql://{config.database.username}:{config.database.password}@{config.database.host}:{config.database.port}/{config.database.db_name}?charset=utf8mb4"
)
