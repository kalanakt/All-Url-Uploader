from pathlib import Path

from config import Settings


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "token")
    monkeypatch.setenv("OWNER_ID", "42")
    monkeypatch.setenv("AUTH_USERS", "1 2 42")
    monkeypatch.setenv("DOWNLOAD_LOCATION", "./tmp-downloads")
    monkeypatch.setenv("CHUNK_SIZE", "128")

    settings = Settings.from_env()

    assert settings.bot_token == "token"
    assert settings.owner_id == 42
    assert settings.auth_users == {1, 2, 42}
    assert settings.download_location == Path("./tmp-downloads")
    assert settings.chunk_size == 131072
