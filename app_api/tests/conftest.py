from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
import pathlib

from core.cmd_utils import load_app_settings
from app_api.app import create_app, AppSettings


@pytest.fixture()
def client() -> Iterator[TestClient]:
    default_config_path = (
            pathlib.Path(__file__).resolve().parent.parent /
            "src" / "app_api" / "configs" / "local.yaml")

    settings = load_app_settings(AppSettings,
                                 ["--config", str(default_config_path)])
    test_app = create_app(settings)

    with TestClient(test_app) as test_client:
        yield test_client
