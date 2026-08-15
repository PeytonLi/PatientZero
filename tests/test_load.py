"""HydraDB load. Nodes are {id} plus one label; rel maps lead with id. Fake session, no Bolt."""

import json
from pathlib import Path

from patient_zero.cypher import PRELIMINARY_BATCH_SIZE
from patient_zero.emit import write_graph
from patient_zero.ids import hydra_id
from patient_zero.loader import load_from_dir, load_graph, load_plan


class FakeSession:
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    def run(self, query, **kwargs):
        self.calls.append((query, kwargs))
        return self

    def consume(self):
        return None


def test_load_graph_upserts_labeled_nodes_before_bitemporal_edges():
    session = FakeSession()
    tables = {
        "packages": [{"pid": "npm:a", "ecosystem": "npm", "name": "a"}],
        "versions": [
            {"vid": "npm:a@1", "pid": "npm:a"},
            {"vid": "npm:b@1", "pid": "npm:b"},
        ],
        "maintainers": [],
        "repos": [],
        "workflows": [],
        "services": [],
        "advisories": [],
        "edges_depends_on": [
            {
                "src_vid": "npm:a@1",
                "dst_vid": "npm:b@1",
                "range": "^1",
                "resolved_version": "1",
                "valid_from": 10,
                "valid_to": 4102444800,
            }
        ],
        "edges_pins": [],
        "edges_maintains": [],
        "edges_published_from": [],
        "edges_has_workflow": [],
        "edges_publishes_via_oidc": [],
        "edges_affects": [],
    }
    summary = load_graph(session, tables)
    queries = [q for q, _ in session.calls]
    version_i = next(i for i, q in enumerate(queries) if "SET a:Version" in q)
    package_i = next(i for i, q in enumerate(queries) if "SET a:Package" in q)
    edge_i = next(i for i, q in enumerate(queries) if ":DEPENDS_ON" in q and "CREATE" in q)
    assert package_i < edge_i
    assert version_i < edge_i
    version_rows = next(kw["rows"] for q, kw in session.calls if "SET a:Version" in q)
    assert {row["id"] for row in version_rows} == {
        hydra_id("npm:a@1"),
        hydra_id("npm:b@1"),
    }
    edge_q, edge_kw = next((q, kw) for q, kw in session.calls if ":DEPENDS_ON" in q and "CREATE" in q)
    assert edge_q.index("id: row.eid") < edge_q.index("valid_from")
    assert edge_kw["rows"][0]["src"] == hydra_id("npm:a@1")
    assert edge_kw["rows"][0]["dst"] == hydra_id("npm:b@1")
    assert edge_kw["rows"][0]["vf"] == 10
    assert edge_kw["rows"][0]["vt"] == 4102444800
    assert summary["nodes"] >= 3
    assert summary["edges"] == 1
    assert summary["batch_size"] == PRELIMINARY_BATCH_SIZE


def test_load_graph_splits_unwinds_at_batch_size():
    session = FakeSession()
    versions = [{"vid": f"npm:p@{i}"} for i in range(1001)]
    tables = {
        "versions": versions,
        "packages": [],
        "maintainers": [],
        "repos": [],
        "workflows": [],
        "services": [],
        "advisories": [],
        "edges_depends_on": [],
        "edges_pins": [],
        "edges_maintains": [],
        "edges_published_from": [],
        "edges_has_workflow": [],
        "edges_publishes_via_oidc": [],
        "edges_affects": [],
    }
    load_graph(session, tables, batch_size=1000)
    version_calls = [kw["rows"] for q, kw in session.calls if "SET a:Version" in q]
    assert [len(rows) for rows in version_calls] == [1000, 1]


def test_load_from_dir_reads_parquet_ids(tmp_path: Path):
    write_graph(
        tmp_path,
        {
            "packages": [{"pid": "npm:a", "ecosystem": "npm", "name": "a"}],
            "versions": [{"vid": "npm:a@1", "pid": "npm:a", "ecosystem": "npm", "name": "a", "version": "1"}],
            "edges_maintains": [{"mid": "npm:t", "pid": "npm:a"}],
            "maintainers": [{"mid": "npm:t", "ecosystem": "npm", "login": "t"}],
        },
    )
    session = FakeSession()
    summary = load_from_dir(session, tmp_path)
    ids = []
    for q, kw in session.calls:
        if "SET a:Package" in q:
            ids.extend(row["id"] for row in kw["rows"])
    assert hydra_id("npm:a") in ids
    assert summary["nodes"] >= 3
    assert summary["edges"] >= 1


def test_load_graph_merges_edge_endpoints_missing_from_node_tables():
    session = FakeSession()
    tables = {
        "packages": [],
        "versions": [],
        "maintainers": [],
        "repos": [],
        "workflows": [
            {
                "wid": "github:mistralai/client-python:.github/workflows/ci.yml",
                "rid": "github:mistralai/client-python",
            }
        ],
        "services": [],
        "advisories": [],
        "edges_depends_on": [],
        "edges_pins": [],
        "edges_maintains": [],
        "edges_published_from": [],
        "edges_has_workflow": [
            {
                "rid": "github:mistralai/client-python",
                "wid": "github:mistralai/client-python:.github/workflows/ci.yml",
            }
        ],
        "edges_publishes_via_oidc": [],
        "edges_affects": [],
    }
    load_graph(session, tables)
    repo_ids = [
        row["id"]
        for q, kw in session.calls
        if "SET a:Repo" in q
        for row in kw["rows"]
    ]
    assert hydra_id("github:mistralai/client-python") in repo_ids


def test_checkpoint_skips_already_written_batches(tmp_path: Path):
    tables = {
        "versions": [{"vid": f"npm:p@{i}"} for i in range(5)],
        "packages": [],
        "maintainers": [],
        "repos": [],
        "workflows": [],
        "services": [],
        "advisories": [],
        "edges_depends_on": [],
        "edges_pins": [],
        "edges_maintains": [],
        "edges_published_from": [],
        "edges_has_workflow": [],
        "edges_publishes_via_oidc": [],
        "edges_affects": [],
    }
    checkpoint = tmp_path / "load.json"
    session = FakeSession()
    load_graph(session, tables, batch_size=3, checkpoint_path=checkpoint)
    first = len(session.calls)
    assert first > 0
    load_graph(session, tables, batch_size=3, checkpoint_path=checkpoint)
    assert len(session.calls) == first
    assert checkpoint.is_file()
    payload = json.loads(checkpoint.read_text(encoding="utf-8"))
    assert payload["status"] == "complete"


def test_load_plan_skips_when_sentinel_present_and_complete():
    assert load_plan(sentinel_exists=True, checkpoint={"status": "complete"}) == "skip"


def test_load_plan_skips_when_sentinel_present_without_checkpoint():
    assert load_plan(sentinel_exists=True, checkpoint=None) == "skip"


def test_load_plan_resumes_partial_checkpoint():
    assert load_plan(
        sentinel_exists=True, checkpoint={"status": "in_progress", "done": ["nodes:Package:0"]}
    ) == "resume"


def test_load_plan_resets_when_volume_was_wiped():
    assert load_plan(sentinel_exists=False, checkpoint={"status": "complete"}) == "reset"
    assert load_plan(sentinel_exists=False, checkpoint=None) == "reset"
