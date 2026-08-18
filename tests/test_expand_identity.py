"""On-demand ingest: expand the slice around one credential, not the whole registry."""

from patient_zero.catalog import Catalog
from patient_zero.engine import Engine
from test_catalog import IOC, TABLES


def test_expand_unknown_identity_adds_nothing():
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    engine = Engine(catalog=cat, run_paths=lambda _q, _p: [])
    body = engine.expand(stable_id="npm:nobody", search={"objects": []})
    assert body["found"] is False
    assert body["added"] == 0


def test_expand_adds_new_package_from_search():
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    engine = Engine(catalog=cat, run_paths=lambda _q, _p: [])
    search = {
        "objects": [
            {"package": {"name": "@tanstack/react-query"}},
            {"package": {"name": "@tanstack/query-core"}},
        ]
    }
    body = engine.expand(stable_id="npm:tannerlinsley", search=search)
    assert body["found"] is True
    assert body["added"] == 1
    pids = [row["pid"] for row in body["packages"]]
    assert "npm:@tanstack/query-core" in pids
    identity = engine.identity(stable_id="npm:tannerlinsley")
    assert "npm:@tanstack/query-core" in [row["pid"] for row in identity["packages"]]


def test_expand_reads_cached_search_when_search_omitted(tmp_path):
    import json

    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    (tmp_path / "tannerlinsley.json").write_text(
        json.dumps({"objects": [{"package": {"name": "left-pad"}}]}),
        encoding="utf-8",
    )
    engine = Engine(
        catalog=cat,
        run_paths=lambda _q, _p: [],
        searches_dir=tmp_path,
    )
    body = engine.expand(stable_id="npm:tannerlinsley")
    assert body["added"] == 1
    assert "npm:left-pad" in [row["pid"] for row in body["packages"]]
