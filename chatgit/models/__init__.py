from datetime import datetime

import databases
import sqlalchemy
from ormar import DateTime, Integer, Model, ModelMeta

from chatgit.common.common import Config

db_config = Config.database

database = databases.Database(f"mysql://{db_config.username}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.db_name}")
metadata = sqlalchemy.MetaData()


class BaseMeta(ModelMeta):
    metadata = metadata
    database = database


class OrmarBaseModel(Model):
    id: int = Integer(primary_key=True, autoincrement=True)
    created_at: datetime = DateTime(default=datetime.utcnow())
    updated_at: datetime = DateTime(default=datetime.utcnow())
