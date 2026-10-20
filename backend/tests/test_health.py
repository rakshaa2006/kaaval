"""Tests for GET /api/health and GET /api/ready."""
from __future__ import annotations

from fastapi.testclient import TestClient


class TestHealth:
    def test_health_returns_200(self, client: TestClient) -> None:
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_status_is_ok(self, client: TestClient) -> None:
        data = client.get("/api/health").json()
        assert data["status"] == "ok"

    def test_health_returns_env(self, client: TestClient) -> None:
        data = client.get("/api/health").json()
        assert data["env"] == "SYNTHETIC_DEMO"

    def test_health_returns_version(self, client: TestClient) -> None:
        data = client.get("/api/health").json()
        assert "version" in data
        assert data["version"]  # non-empty


class TestReady:
    def test_ready_returns_200(self, client: TestClient) -> None:
        response = client.get("/api/ready")
        assert response.status_code == 200

    def test_ready_status_is_ready(self, client: TestClient) -> None:
        data = client.get("/api/ready").json()
        assert data["status"] == "ready"

    def test_ready_database_is_connected(self, client: TestClient) -> None:
        data = client.get("/api/ready").json()
        assert data["database"] == "connected"
