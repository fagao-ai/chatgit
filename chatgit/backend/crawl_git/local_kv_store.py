import time
from typing import Any, Dict


class LocalKVDatabase:
    def __init__(self) -> None:
        self.data: Dict[str, Dict[str, Any]] = {}

    def set(self, key: str, value: str, ttl: int = None) -> None:
        if ttl is not None:
            expire_timestamp = time.time() + ttl
        else:
            expire_timestamp = None
        self.data[key] = {"value": value, "expire_time": expire_timestamp}

    def get(self, key: str) -> str | None:
        if key in self.data:
            entry = self.data[key]
            if entry["expire_time"] is None or entry["expire_time"] >= time.time():
                return entry["value"]
            else:
                del self.data[key]
        return None

    def delete(self, key: str) -> None:
        if key in self.data:
            del self.data[key]
