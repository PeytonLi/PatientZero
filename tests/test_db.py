"""Bolt URI helpers. No live HydraDB."""

from patient_zero import db


def test_bolt_uri_prefers_explicit(monkeypatch):
    monkeypatch.setenv("HYDRADB_BOLT_URI", "bolt://explicit:7687")
    monkeypatch.setenv("HYDRADB_BOLT_HOST", "ignored")
    assert db._uri() == "bolt://explicit:7687"


def test_bolt_uri_from_host_and_port(monkeypatch):
    monkeypatch.delenv("HYDRADB_BOLT_URI", raising=False)
    monkeypatch.setenv("HYDRADB_BOLT_HOST", "pz-hydradb")
    monkeypatch.setenv("HYDRADB_BOLT_PORT", "7687")
    assert db._uri() == "bolt://pz-hydradb:7687"


def test_bolt_uri_defaults_to_localhost(monkeypatch):
    monkeypatch.delenv("HYDRADB_BOLT_URI", raising=False)
    monkeypatch.delenv("HYDRADB_BOLT_HOST", raising=False)
    assert db._uri() == "bolt://127.0.0.1:7687"
