from datetime import datetime

import databases
import sqlalchemy
from ormar import DateTime, Integer, ModelMeta

from chatgit.common import db_url

database = databases.Database(db_url)
metadata = sqlalchemy.MetaData()


class BaseMeta(ModelMeta):
    metadata = metadata
    database = database


class BaseModelMixins:
    id: int = Integer(primary_key=True, autoincrement=True)
    created_at: datetime = DateTime(default=datetime.now())
    updated_at: datetime = DateTime(default=datetime.now())
