from enum import Enum
from typing import TypeAlias


class StrEnum(str, Enum):
    ...


Text: TypeAlias = str

__all__ = "Text"
