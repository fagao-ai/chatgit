from datetime import datetime
from typing import Annotated

import databases
import sqlalchemy
from ormar import DateTime, Integer, Model
from ormar.models.ormar_config import OrmarConfig

from chatgit.common import db_url

base_ormar_config = OrmarConfig(
    metadata=sqlalchemy.MetaData(),
    database=databases.Database(db_url),
)

database = base_ormar_config.database


class BaseModel(Model):
    ormar_config = base_ormar_config.copy(abstract=True)

    id: Annotated[int, Integer(primary_key=True, autoincrement=True)]
    created_at: datetime = DateTime(default=datetime.now())
    updated_at: datetime = DateTime(default=datetime.now())
