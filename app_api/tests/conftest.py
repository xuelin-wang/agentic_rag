from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app_api.main import build_app


@pytest.fixture()
def client() -> Iterator[TestClient]:
    test_app, settings = build_app()

    with TestClient(test_app) as test_client:
        yield test_client
