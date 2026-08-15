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


def test_health_and_static_index(client: TestClient) -> None:
    health = _assert_envelope(client.get("/api/health").json())
    assert health["ok"] is True
    assert "hydradb_connected" in health
    assert "graph_loaded" in health
    assert "ready" in health
    assert health["mode"] in ("live", "degraded")
    assert isinstance(health["catalog_nodes"], int)
    assert health["catalog_nodes"] >= 1
    # Unit tests do not start HydraDB; the API must still answer and not
    # claim to be a live loaded graph.
    if not health["hydradb_connected"]:
        assert health["ready"] is False
        assert health["mode"] == "degraded"
    page = client.get("/")
    assert page.status_code == 200
    assert b"Patient" in page.content
    assert b"play-clock" in page.content


def test_invalid_forecast_params_are_422(client: TestClient) -> None:
    assert client.post("/api/forecast", json={"topology": "social"}).status_code == 422
    assert client.post("/api/forecast", json={"k": 0}).status_code == 422
    assert client.post("/api/forecast", json={"max_hops": 0}).status_code == 422


def test_all_envelopes_json_serialize(client: TestClient) -> None:
    import json

    for path in POST_ROUTES:
        json.dumps(client.post(path, json={}).json())
    for path in GET_ROUTES + ("/api/health",):
        json.dumps(client.get(path).json())


def test_meta_exposes_seed_pids_and_blast_with_a_version(client: TestClient) -> None:
    body = _assert_envelope(client.get("/api/meta").json())
    assert body["seed_pids"] == ["npm:@tanstack/react-query"]
    assert body["default_blast"]["name"] == "@tanstack/react-query"
    assert body["default_blast"]["version"] == "5.101.4"
    assert body["default_sid"] == "svc:app"
    assert body["finding_vids"] == []


def test_timeline_includes_ioc_nodes(client: TestClient) -> None:
    body = _assert_envelope(client.get("/api/timeline").json())
    ids = {n["id"] for n in body["nodes"]}
    assert "npm:@tanstack/react-query" in ids


def test_omitted_seeds_use_catalog_but_explicit_empty_does_not(client: TestClient) -> None:
    omitted = _assert_envelope(client.post("/api/forecast", json={"topology": "trust"}).json())
    assert omitted["stats"]["seeds"] == 1
    empty = _assert_envelope(
        client.post("/api/forecast", json={"seeds": [], "topology": "trust"}).json()
    )
    assert empty["stats"]["seeds"] == 0
    assert empty["predictions"] == []


def test_leverage_exposes_packages_at_risk_not_lockfile_services(client: TestClient) -> None:
    body = _assert_envelope(client.get("/api/leverage").json())
    assert "mincut" in body
    assert body["stats"]["cover"] == "greedy"
    for row in body["ranked"]:
        assert "packages_at_risk" in row
