import json
import time
import uuid
from typing import Any, Dict, Optional

from redis.asyncio import Redis

from app.models.run import RunRecord


class RunStore:
    """
    M0 Run store backed by Redis.
    Storage strategy (M0):
    - key: run:{run_id}
    - value: JSON string for RunRecord
    """

    def __init__(self, redis: Redis, ttl_s: int = 86400):
        self._r = redis
        self._ttl_s = int(ttl_s)

    @staticmethod
    def _key(run_id: str) -> str:
        return f"run:{run_id}"

    async def create_run(self, request_dict: Dict[str, Any]) -> RunRecord:
        run_id = uuid.uuid4().hex
        now = int(time.time())
        record = RunRecord(
            run_id=run_id,
            status="CREATED",
            created_at=now,
            request=request_dict,
            result=None,
            error=None,
        )
        await self.save_run(record)
        return record

    async def save_run(self, record: RunRecord) -> None:
        key = self._key(record.run_id)
        payload = record.model_dump()
        await self._r.set(key, json.dumps(payload), ex=self._ttl_s)

    async def load_run(self, run_id: str) -> Optional[RunRecord]:
        key = self._key(run_id)
        raw = await self._r.get(key)
        if raw is None:
            return None
        try:
            data = json.loads(raw)
            return RunRecord.model_validate(data)
        except Exception:
            # If corrupted data, treat as not found (keeps M0 simple)
            return None

    async def save_state(self, run_id: str, state_dict: dict, last_node: str) -> None:
        run = load_run(run_id)
        if raw is None:
            return None
        

    async def load_state(self, run_id: str) -> dict | None: 
    