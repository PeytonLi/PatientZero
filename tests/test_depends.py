"""deps.dev forward graphs. Wrong from/to would invert blast radius."""

from patient_zero.assemble import SENTINEL_VALID_TO
from patient_zero.depends import depends_on_edges

GRAPH = {
    "nodes": [
        {
            "versionKey": {"system": "NPM", "name": "@tanstack/react-query", "version": "5.90.2"},
            "relation": "SELF",
        },
        {
            "versionKey": {"system": "NPM", "name": "@tanstack/query-core", "version": "5.90.2"},
            "relation": "DIRECT",
        },
    ],
    "edges": [{"fromNode": 0, "toNode": 1, "requirement": "^5.90.2"}],
}


def test_depends_on_maps_from_dependent_to_dependency():
    rows = depends_on_edges(GRAPH, published_at=1778527239)
    assert rows == [
        {
            "src_vid": "npm:@tanstack/react-query@5.90.2",
            "dst_vid": "npm:@tanstack/query-core@5.90.2",
            "range": "^5.90.2",
            "resolved_version": "5.90.2",
            "valid_from": 1778527239,
            "valid_to": SENTINEL_VALID_TO,
        }
    ]


def test_depends_on_skips_graph_with_no_edges():
    leaf = {
        "nodes": [
            {
                "versionKey": {"system": "NPM", "name": "@tanstack/query-core", "version": "5.90.2"},
                "relation": "SELF",
            }
        ],
        "edges": [],
    }
    assert depends_on_edges(leaf, published_at=1) == []


def test_depends_on_uses_sentinel_when_published_at_missing():
    rows = depends_on_edges(GRAPH, published_at=None)
    assert rows[0]["valid_from"] == 0
    assert rows[0]["valid_to"] == SENTINEL_VALID_TO
