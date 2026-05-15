"""Pytest configuration and shared fixtures."""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from speech_io_hub.server.app import create_app

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("LOG_LEVEL", "DEBUG")


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_client() -> TestClient:
    return TestClient(create_app())
