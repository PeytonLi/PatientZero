"""Shape tests against the wired API. Fake engine — no HydraDB required."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from patient_zero import api
from patient_zero.api import app
from patient_zero.catalog import Catalog
from patient_zero.engine import Engine
from test_catalog import IOC, TABLES

POST_ROUTES = (
    "/api/blast-radius",
    "/api/forecast",
    "/api/index-case",
    "/api/reachability",
)
GET_ROUTES = (
    "/api/leverage",
    "/api/evidence",
    "/api/timeline",
    "/api/meta",
)


@pytest.fixture
def client():
    catalog = Catalog.from_tables(TABLES, ioc_records=IOC)
    api.configure(Engine(catalog=catalog, run_paths=lambda _q, _p: []))
    with TestClient(app) as c:
        yield c
    api.configure(None)


def _assert_envelope(body: object) -> dict:
    assert isinstance(body, dict)
    assert "stub" in body
    assert "cypher" in body
    assert "latency_ms" in body
    assert isinstance(body["cypher"], str)
    assert isinstance(body["latency_ms"], (int, float))
    return body


@pytest.mark.parametrize("path", POST_ROUTES)
def test_post_routes_200_envelope(client: TestClient, path: str) -> None:
    response = client.post(path, json={})
    assert response.status_code == 200, path
    _assert_envelope(response.json())


@pytest.mark.parametrize("path", GET_ROUTES)
def test_get_routes_200_envelope(client: TestClient, path: str) -> None:
    response = client.get(path)
    assert response.status_code == 200, path
    _assert_envelope(response.json())


def test_wired_responses_are_not_stub(client: TestClient) -> None:
    body = _assert_envelope(client.post("/api/blast-radius", json={}).json())
    assert body["stub"] is False
    assert "sourceNode: $sourceNode" in body["cypher"]
    assert "sourceProperty" not in body["cypher"]
    assert body["services"] == []


def test_evidence_precision_fields_are_json_null(client: TestClient) -> None:
    body = _assert_envelope(client.get("/api/evidence").json())
    for key in ("precision_trust", "precision_dependency"):
        precision = body[key]
        assert precision["precision_at_10"] is None
        assert precision["precision_at_50"] is None
        assert precision["precision_at_100"] is None
        assert precision["recall_at_100"] is None
    assert body["r0_trust"] is None
    assert body["r0_dependency"] is None


def test_forecast_dependency_is_negative_control(client: TestClient) -> None:
    body = _assert_envelope(
        client.post("/api/forecast", json={"topology": "dependency"}).json()
    )
    assert body["stats"]["is_negative_control"] is True
    assert body["stats"]["topology"] == "dependency"
    assert body["stats"]["precision_at_k"] is None
    assert "DEPENDS_ON" in body["cypher"]
    assert "MAINTAINS" not in body["cypher"]
