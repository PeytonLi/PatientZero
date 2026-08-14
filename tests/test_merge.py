"""Merge and node closure. MATCH-CREATE fails if an edge endpoint vid was never a node."""

from patient_zero.assemble import assemble
from patient_zero.merge import ensure_endpoint_nodes, merge_tables


def test_merge_tables_dedupes_on_pid():
    a = {
        "packages": [{"pid": "npm:a", "ecosystem": "npm", "name": "a"}],
        "edges_maintains": [{"mid": "npm:t", "pid": "npm:a"}],
    }
    b = {
        "packages": [
            {"pid": "npm:a", "ecosystem": "npm", "name": "a"},
            {"pid": "npm:b", "ecosystem": "npm", "name": "b"},
        ],
        "edges_maintains": [{"mid": "npm:t", "pid": "npm:a"}],
    }
    m = merge_tables(a, b)
    assert [r["pid"] for r in m["packages"]] == ["npm:a", "npm:b"]
    assert m["edges_maintains"] == [{"mid": "npm:t", "pid": "npm:a"}]


def test_ensure_endpoint_nodes_adds_missing_depends_on_versions():
    tables = assemble(
        [
            {
                "pid": "npm:@tanstack/react-query",
                "vid": "npm:@tanstack/react-query@5.90.2",
                "ecosystem": "npm",
                "split": "seed",
            }
        ],
        [],
    )
    tables["edges_depends_on"] = [
        {
            "src_vid": "npm:@tanstack/react-query@5.90.2",
            "dst_vid": "npm:@tanstack/query-core@5.90.2",
            "range": "^5.90.2",
            "resolved_version": "5.90.2",
            "valid_from": 0,
            "valid_to": 4102444800,
        }
    ]
    ensure_endpoint_nodes(tables)
    vids = {r["vid"] for r in tables["versions"]}
    pids = {r["pid"] for r in tables["packages"]}
    assert "npm:@tanstack/query-core@5.90.2" in vids
    assert "npm:@tanstack/query-core" in pids
