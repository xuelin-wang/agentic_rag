from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from core.settings import load_dataclass_from_yaml


@dataclass(slots=True)
class Credentials:
    username: str
    password: str


@dataclass(slots=True)
class DatabaseConfig:
    host: str
    port: int
    credentials: Credentials


@dataclass(slots=True)
class AppConfig:
    database: DatabaseConfig
    debug: bool = False


def write_yaml(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_loads_nested_values_with_env_fallback(tmp_path, monkeypatch):
    yaml_path = write_yaml(
        tmp_path / "config.yaml",
        """
        database:
          host: api.internal
          port: 5432
          credentials:
            username: ""
            password: ""
        """,
    )

    monkeypatch.setenv("DATABASE__CREDENTIALS__USERNAME", "service-user")
    monkeypatch.setenv("DATABASE__CREDENTIALS__PASSWORD", "secret")
    monkeypatch.setenv("DEBUG", "true")

    config = load_dataclass_from_yaml(AppConfig, yaml_path)

    assert config.database.host == "api.internal"
    assert config.database.port == 5432
    assert config.database.credentials.username == "service-user"
    assert config.database.credentials.password == "secret"
    assert config.debug is True


def test_missing_required_value_without_env_raises(tmp_path):
    yaml_path = write_yaml(
        tmp_path / "config.yaml",
        """
        database:
          port: 15432
          credentials:
            password: supersecret
        """,
    )

    with pytest.raises(ValueError) as exc:
        load_dataclass_from_yaml(AppConfig, yaml_path)

    assert "DATABASE__HOST" in str(exc.value)


def test_non_mapping_for_nested_field_errors(tmp_path):
    yaml_path = write_yaml(
        tmp_path / "config.yaml",
        "database: []\n",
    )

    with pytest.raises(TypeError):
        load_dataclass_from_yaml(AppConfig, yaml_path)
