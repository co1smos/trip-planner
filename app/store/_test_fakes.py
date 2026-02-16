import json
from typing import Any, Dict, Optional


class FakeRedis:
    """
    Minimal async Redis fake that supports:
    - ping()
    - get(key)
    - set(key, value, ex=None)
    """
    def __init__(self, ping_ok: bool = True):
        self._data: Dict[str, str] = {}
        self._ping_ok = ping_ok

    async def ping(self) -> bool:
        if not self._ping_ok:
            raise RuntimeError("redis down")
        return True

    async def get(self, key: str) -> Optional[str]:
        return self._data.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> None:
        # We ignore TTL in M0 fake (not needed for unit tests)
        self._data[key] = value

    # Convenience helpers for tests
    def raw_set_json(self, key: str, obj: Any) -> None:
        self._data[key] = json.dumps(obj)

    def raw_set_str(self, key: str, s: str) -> None:
        self._data[key] = s
