import os
# from pydantic.main import BaseModel

# from chatgit.common import PROJECT_PATH
# from chatgit.common.my_base_settings import MyBaseSettings


# class Database(BaseModel):
#     host: str
#     port: int
#     username: str
#     password: str
#     db_name: str


# class QdrantConnection(BaseModel):
#     url: str | None = None
#     host: str | None = None
#     port: int | None = None
#     memory: bool | None = False


# class CrawlConfig(BaseModel):
#     start_page: int
#     proxy_limit: int


# class Config(MyBaseSettings):
#     database: Database
#     qdrant: QdrantConnection = QdrantConnection()
#     crawl: CrawlConfig

#     class Config:
#         env_file = PROJECT_PATH / "chatgit/config/config.dev.toml"


# CONFIG_DIR = PROJECT_PATH / "chatgit/config"

# ENV = os.getenv("ENV", "prod")

# if ENV == "dev":
#     Config.Config.env_file = CONFIG_DIR / "config.dev.toml"
# elif ENV == "prod":
#     Config.Config.env_file = CONFIG_DIR / "config.prod.toml"

# config = Config()
DB_ENABLE = os.getenv("CHATGIT_DB_ENABLE", False)
DB_USERNAME = os.getenv("CHATGIT_DB_USERNAME", "postgres")
DB_PASSWORD = os.getenv("CHATGIT_DB_PASSWORD", "")
DB_HOST = os.getenv("CHATGIT_DB_HOST", "localhost")
DB_PORT = os.getenv("CHATGIT_DB_PORT", "5432")
DB_NAME = os.getenv("CHATGIT_DB_NAME", "chatgit")
db_url = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
