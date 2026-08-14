"""Engine over bounded algo.SSpaths. Fake runner — no Bolt in unit tests."""

from __future__ import annotations

from patient_zero.catalog import Catalog
from patient_zero.engine import Engine
from patient_zero.ids import hydra_id
from test_catalog import IOC, SENTINEL, TABLES, WORM


class FakeNode:
    def __init__(self, hid: int, label: str):
        self.element_id = str(hid)
        self.labels = frozenset({label})
        self._props: dict = {}

    def get(self, key, default=None):
        return self._props.get(key, default)


class FakeRel:
    def __init__(self, typ: str, *, vf: int | None = None, vt: int | None = None):
        self.type = typ
        self._props = {}
        if vf is not None:
            self._props["valid_from"] = vf
            self._props["valid_to"] = vt

    def get(self, key, default=None):
        return self._props.get(key, default)

    def __getitem__(self, key):
        return self._props[key]


class FakePath:
    def __init__(self, nodes: list[FakeNode], rels: list[FakeRel]):
        self.nodes = nodes
        self.relationships = rels


def _node(stable: str, label: str) -> FakeNode:
    return FakeNode(hydra_id(stable), label)


def test_blast_radius_keeps_service_paths_inside_the_window_only():
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    vid = "npm:@tanstack/react-query@5.101.4"
    svc = "svc:app"
    path = FakePath(
        [_node(vid, "Version"), _node(svc, "Service")],
        [FakeRel("PINS", vf=WORM + 100, vt=SENTINEL)],
    )

    def run(cypher: str, params: dict):
        assert "sourceNode: $sourceNode" in cypher
        assert params["sourceNode"] == hydra_id(vid)
        return [path]

    engine = Engine(catalog=cat, run_paths=run)
    closed = engine.blast_radius(
        ecosystem="npm",
        name="@tanstack/react-query",
        version="5.0.1",
        window_start=WORM,
        window_end=WORM + 50,
        max_hops=4,
        limit=50,
    )
    assert closed["services"] == []
    assert closed["stats"]["source_vid"] == vid

    open_ = engine.blast_radius(
        ecosystem="npm",
        name="@tanstack/react-query",
        version="5.0.1",
        window_start=WORM,
        window_end=WORM + 200,
        max_hops=4,
        limit=50,
    )
    assert len(open_["services"]) == 1
    hit = open_["services"][0]
    assert hit["sid"] == svc
    assert hit["name"] == "app"
    assert hit["exposed_at"] == WORM + 100
    assert hit["path"] == [vid, svc]


def test_forecast_trust_ranks_co_maintained_package_not_in_seeds():
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    seed = "npm:@tanstack/react-query"
    neighbour = "npm:@tanstack/store"
    mid = "npm:tannerlinsley"
    path = FakePath(
        [_node(seed, "Package"), _node(mid, "Maintainer"), _node(neighbour, "Package")],
        [FakeRel("MAINTAINS"), FakeRel("MAINTAINS")],
    )

    def run(cypher: str, params: dict):
        assert "MAINTAINS" in cypher
        if params["sourceNode"] == hydra_id(seed):
            return [path]
        return []

    engine = Engine(catalog=cat, run_paths=run)
    body = engine.forecast(seeds=[seed], as_of=WORM + 360, k=10, topology="trust", max_hops=3, limit=50)
    assert body["stats"]["is_negative_control"] is False
    assert body["predictions"][0]["pid"] == neighbour
    assert body["predictions"][0]["justification_path"] == [seed, mid, neighbour]
    assert body["stats"]["precision_at_k"] is None


def test_forecast_dependency_is_negative_control_and_uses_t1_rels():
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    seen: list[str] = []

    def run(cypher: str, params: dict):
        seen.append(cypher)
        return []

    engine = Engine(catalog=cat, run_paths=run)
    body = engine.forecast(
        seeds=["npm:@tanstack/react-query"],
        as_of=WORM + 360,
        k=10,
        topology="dependency",
        max_hops=3,
        limit=50,
    )
    assert body["stats"]["is_negative_control"] is True
    assert body["predictions"] == []
    assert any("DEPENDS_ON" in q for q in seen)
    assert any("MAINTAINS" not in q for q in seen)


def test_index_case_ranks_shared_maintainer_and_measures_origin():
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    observed = "npm:@tanstack/react-query"
    mid = "npm:tannerlinsley"
    path = FakePath(
        [_node(observed, "Package"), _node(mid, "Maintainer")],
        [FakeRel("MAINTAINS")],
    )

    def run(cypher: str, params: dict):
        return [path] if params["sourceNode"] == hydra_id(observed) else []

    engine = Engine(catalog=cat, run_paths=run)
    body = engine.index_case(observed=[observed], as_of=WORM + 360, k=5, max_hops=4, limit=50)
    assert body["candidates"][0]["id"] == mid
    assert body["candidates"][0]["kind"] == "maintainer"
    assert body["stats"]["true_origin_rank"] == 1


def test_reachability_is_pin_join_plus_install_hooks():
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    engine = Engine(catalog=cat, run_paths=lambda q, p: [])
    body = engine.reachability(
        sid="svc:app",
        finding_vids=["npm:lodash@4.17.21", "npm:@tanstack/react-query@5.101.4"],
        as_of=WORM + 200,
    )
    by_vid = {v["vid"]: v for v in body["verdicts"]}
    assert by_vid["npm:lodash@4.17.21"]["tier"] == "install"
    assert by_vid["npm:lodash@4.17.21"]["evidence"]["install_hooks"] == ["postinstall"]
    assert by_vid["npm:@tanstack/react-query@5.101.4"]["tier"] == "none"
    too_early = engine.reachability(
        sid="svc:app",
        finding_vids=["npm:lodash@4.17.21"],
        as_of=WORM,
    )
    assert too_early["verdicts"] == []


def test_evidence_stays_null_until_a_forecast_returns_paths():
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    engine = Engine(catalog=cat, run_paths=lambda q, p: [])
    body = engine.evidence()
    assert body["precision_trust"]["precision_at_10"] is None
    assert body["precision_dependency"]["precision_at_10"] is None
    assert body["r0_trust"] is None
    assert body["stats"]["measured"] is False


def test_evidence_precision_is_scored_against_validation_pids():
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    seed = "npm:@tanstack/react-query"
    neighbour = "npm:@tanstack/store"
    path = FakePath(
        [_node(seed, "Package"), _node("npm:tannerlinsley", "Maintainer"), _node(neighbour, "Package")],
        [FakeRel("MAINTAINS"), FakeRel("MAINTAINS")],
    )

    def run(cypher: str, params: dict):
        if "MAINTAINS" in cypher and params["sourceNode"] == hydra_id(seed):
            return [path]
        return []

    engine = Engine(catalog=cat, run_paths=run)
    body = engine.evidence(k=10)
    assert body["stats"]["measured"] is True
    assert body["precision_trust"]["precision_at_10"] == 1.0
    assert body["precision_dependency"]["precision_at_10"] == 0.0
    assert body["r0_trust"] is None
