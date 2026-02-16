import os

from app.config import Settings, get_settings


def test_get_settings_defaults(monkeypatch):
    # Ensure no env overrides
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.delenv("RUN_TTL_S", raising=False)

    s = get_settings()
    assert isinstance(s, Settings)
    assert s.REDIS_URL.startswith("redis://")
    assert isinstance(s.RUN_TTL_S, int)


def test_get_settings_from_env(monkeypatch):
    monkeypatch.setenv("REDIS_URL", "redis://example:6379/9")
    monkeypatch.setenv("RUN_TTL_S", "123")

    s = get_settings()
    assert s.REDIS_URL == "redis://example:6379/9"
    assert s.RUN_TTL_S == 123
