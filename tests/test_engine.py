"""Engine over bounded algo.SSpaths. Fake runner — no Bolt in unit tests."""

from __future__ import annotations

from copy import deepcopy

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
    assert body["stats"]["paths_returned"] == 1


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
    assert body["r0_trust"] == 1.0
    assert body["r0_dependency"] == 0.0
    assert body["trust_paths"] == 1
    assert body["control_paths"] == 0
    assert body["control_note"] == "identical SSpaths, relTypes swapped"


def test_evidence_r0_is_mean_validation_pids_reached_per_seed():
    """R0 = mean over seeds of |validation pids reached from that seed|. Not a hardcoded constant."""
    seed_a = "npm:seed-a"
    seed_b = "npm:seed-b"
    val_one = "npm:val-one"
    val_two = "npm:val-two"
    mid = "npm:zzz-bridge"
    tables = deepcopy(TABLES)
    tables["packages"] = [_pkg(seed_a), _pkg(seed_b), _pkg(val_one), _pkg(val_two)]
    tables["maintainers"] = [_maint(mid)]
    tables["edges_maintains"] = [
        {"mid": mid, "pid": seed_a},
        {"mid": mid, "pid": val_one},
        {"mid": mid, "pid": val_two},
        {"mid": mid, "pid": seed_b},
    ]
    ioc = [
        {"pid": seed_a, "split": "seed", "first_seen_utc": WORM},
        {"pid": seed_b, "split": "seed", "first_seen_utc": WORM},
        {"pid": val_one, "split": "validation", "first_seen_utc": WORM + 2000},
        {"pid": val_two, "split": "validation", "first_seen_utc": WORM + 2000},
    ]
    cat = Catalog.from_tables(tables, ioc_records=ioc)

    def run(cypher: str, params: dict):
        if "MAINTAINS" not in cypher:
            return []
        if params["sourceNode"] == hydra_id(seed_a):
            return [
                FakePath(
                    [_node(seed_a, "Package"), _node(mid, "Maintainer"), _node(val_one, "Package")],
                    [FakeRel("MAINTAINS"), FakeRel("MAINTAINS")],
                ),
                FakePath(
                    [_node(seed_a, "Package"), _node(mid, "Maintainer"), _node(val_two, "Package")],
                    [FakeRel("MAINTAINS"), FakeRel("MAINTAINS")],
                ),
            ]
        return []

    engine = Engine(catalog=cat, run_paths=run)
    body = engine.evidence(k=10)
    # seed_a reaches 2 validation pids, seed_b reaches 0 → mean 1.0
    assert body["r0_trust"] == 1.0
    assert body["r0_dependency"] == 0.0
    assert body["stats"]["r0_definition"] == "mean validation pids reached per seed"


def test_leverage_greedy_cover_ranks_the_maintainer_who_covers_more_validation_pids():
    seed = "npm:seed-pkg"
    val_a = "npm:val-a"
    val_b = "npm:val-b"
    val_c = "npm:val-c"
    wide = "npm:zzz-wide"
    narrow = "npm:aaa-narrow"
    tables = deepcopy(TABLES)
    tables["packages"] = [_pkg(seed), _pkg(val_a), _pkg(val_b), _pkg(val_c)]
    tables["maintainers"] = [_maint(wide), _maint(narrow)]
    tables["edges_maintains"] = [
        {"mid": wide, "pid": seed},
        {"mid": wide, "pid": val_a},
        {"mid": wide, "pid": val_b},
        {"mid": narrow, "pid": seed},
        {"mid": narrow, "pid": val_c},
    ]
    ioc = [
        {"pid": seed, "split": "seed", "first_seen_utc": WORM},
        {"pid": val_a, "split": "validation", "first_seen_utc": WORM + 2000},
        {"pid": val_b, "split": "validation", "first_seen_utc": WORM + 2000},
        {"pid": val_c, "split": "validation", "first_seen_utc": WORM + 2000},
    ]
    cat = Catalog.from_tables(tables, ioc_records=ioc)

    def run(cypher: str, params: dict):
        if "MAINTAINS" not in cypher:
            return []
        if params["sourceNode"] != hydra_id(seed):
            return []
        return [
            FakePath(
                [_node(seed, "Package"), _node(wide, "Maintainer"), _node(val_a, "Package")],
                [FakeRel("MAINTAINS"), FakeRel("MAINTAINS")],
            ),
            FakePath(
                [_node(seed, "Package"), _node(wide, "Maintainer"), _node(val_b, "Package")],
                [FakeRel("MAINTAINS"), FakeRel("MAINTAINS")],
            ),
            FakePath(
                [_node(seed, "Package"), _node(narrow, "Maintainer"), _node(val_c, "Package")],
                [FakeRel("MAINTAINS"), FakeRel("MAINTAINS")],
            ),
        ]

    engine = Engine(catalog=cat, run_paths=run)
    body = engine.leverage(k=5, max_hops=4, limit=50)
    assert body["ranked"][0]["id"] == wide
    assert body["ranked"][0]["packages_at_risk"] == 2
    assert body["ranked"][1]["id"] == narrow
    assert body["mincut"][0]["id"] == wide
    assert body["stats"]["cover"] == "greedy"
    reachable = 3
    covered = 3
    assert body["stats"]["spread_blocked_pct"] == round(covered / reachable, 4)
    assert body["stats"]["spread_blocked_pct"] == 1.0
    assert body["stats"]["cover_universe"] == "forecast_neighborhood"
    assert body["stats"]["reachable_neighborhood"] == 3
    assert body["stats"]["reachable_validation"] == 3


def test_leverage_mincut_covers_forecast_neighborhood_without_validation():
    seed = "npm:seed-pkg"
    neighbour = "npm:other-pkg"
    wide = "npm:zzz-wide"
    tables = deepcopy(TABLES)
    tables["packages"] = [_pkg(seed), _pkg(neighbour)]
    tables["maintainers"] = [_maint(wide)]
    tables["edges_maintains"] = [
        {"mid": wide, "pid": seed},
        {"mid": wide, "pid": neighbour},
    ]
    ioc = [{"pid": seed, "split": "seed", "first_seen_utc": WORM}]
    cat = Catalog.from_tables(tables, ioc_records=ioc)

    def run(cypher: str, params: dict):
        if "MAINTAINS" not in cypher:
            return []
        if params["sourceNode"] != hydra_id(seed):
            return []
        return [
            FakePath(
                [_node(seed, "Package"), _node(wide, "Maintainer"), _node(neighbour, "Package")],
                [FakeRel("MAINTAINS"), FakeRel("MAINTAINS")],
            )
        ]

    engine = Engine(catalog=cat, run_paths=run)
    body = engine.leverage(k=5, max_hops=4, limit=50)
    assert body["stats"]["reachable_validation"] == 0
    assert body["stats"]["reachable_neighborhood"] == 1
    assert body["mincut"][0]["id"] == wide
    assert body["stats"]["spread_blocked_pct"] == 1.0


def test_forecast_trust_drops_maintains_outside_the_window():
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    seed = "npm:@tanstack/react-query"
    neighbour = "npm:@tanstack/store"
    mid = "npm:tannerlinsley"
    future = FakePath(
        [_node(seed, "Package"), _node(mid, "Maintainer"), _node(neighbour, "Package")],
        [
            FakeRel("MAINTAINS", vf=WORM + 10_000, vt=SENTINEL),
            FakeRel("MAINTAINS", vf=WORM + 10_000, vt=SENTINEL),
        ],
    )

    def run(cypher: str, params: dict):
        if params["sourceNode"] == hydra_id(seed):
            return [future]
        return []

    engine = Engine(catalog=cat, run_paths=run)
    body = engine.forecast(
        seeds=[seed], as_of=WORM + 360, k=10, topology="trust", max_hops=3, limit=50
    )
    assert body["predictions"] == []
    assert body["stats"]["paths_returned"] == 0


def test_timeline_nodes_come_from_ioc_first_seen():
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    engine = Engine(catalog=cat, run_paths=lambda q, p: [])
    body = engine.timeline()
    by_id = {n["id"]: n for n in body["nodes"]}
    assert by_id["npm:@tanstack/react-query"]["at"] == WORM
    assert by_id["npm:@tanstack/react-query"]["role"] == "origin"
    assert by_id["npm:@tanstack/store"]["role"] == "hit"
    assert by_id["npm:@tanstack/store"]["eco"] == "npm"
    assert body["incident_id"] == "may11-tanstack"
    assert body["window_start"] == WORM
    assert body["events"][0]["label"] == "worm begins"


def _pkg(pid: str) -> dict:
    name = pid.split(":", 1)[-1]
    return {"pid": pid, "ecosystem": "npm", "name": name}


def _maint(mid: str) -> dict:
    login = mid.split(":", 1)[-1]
    return {"mid": mid, "ecosystem": "npm", "login": login, "email_domain": None, "twofa": None}


def test_forecast_rare_maintainer_outranks_popular_at_the_same_path_count():
    """Exclusivity: 1/degree. Alphabetical would put aaa-via-popular first."""
    seed = "npm:seed-pkg"
    popular = "npm:aaa-popular"
    rare = "npm:zzz-rare"
    via_popular = "npm:aaa-via-popular"
    via_rare = "npm:zzz-via-rare"
    tables = deepcopy(TABLES)
    tables["packages"] = [
        _pkg(seed),
        _pkg(via_popular),
        _pkg(via_rare),
        *[_pkg(f"npm:dummy-{i}") for i in range(20)],
    ]
    tables["maintainers"] = [_maint(popular), _maint(rare)]
    tables["edges_maintains"] = [
        {"mid": popular, "pid": seed},
        {"mid": popular, "pid": via_popular},
        *[{"mid": popular, "pid": f"npm:dummy-{i}"} for i in range(20)],
        {"mid": rare, "pid": seed},
        {"mid": rare, "pid": via_rare},
    ]
    ioc = [
        {"pid": seed, "split": "seed", "first_seen_utc": WORM},
        {"pid": via_popular, "split": "validation", "first_seen_utc": WORM + 2000},
        {"pid": via_rare, "split": "validation", "first_seen_utc": WORM + 2000},
    ]
    cat = Catalog.from_tables(tables, ioc_records=ioc)
    assert cat.degree(popular) > cat.degree(rare)

    def run(cypher: str, params: dict):
        if params["sourceNode"] != hydra_id(seed):
            return []
        return [
            FakePath(
                [_node(seed, "Package"), _node(popular, "Maintainer"), _node(via_popular, "Package")],
                [FakeRel("MAINTAINS"), FakeRel("MAINTAINS")],
            ),
            FakePath(
                [_node(seed, "Package"), _node(rare, "Maintainer"), _node(via_rare, "Package")],
                [FakeRel("MAINTAINS"), FakeRel("MAINTAINS")],
            ),
        ]

    engine = Engine(catalog=cat, run_paths=run)
    body = engine.forecast(seeds=[seed], as_of=WORM + 360, k=10, topology="trust", max_hops=3, limit=50)
    ranked = [row["pid"] for row in body["predictions"]]
    assert ranked[0] == via_rare
    assert via_popular in ranked
    assert body["predictions"][0]["score"] > body["predictions"][1]["score"]


def test_forecast_popularity_rank_inverts_exclusivity():
    seed = "npm:seed-pkg"
    popular = "npm:aaa-popular"
    rare = "npm:zzz-rare"
    via_popular = "npm:aaa-via-popular"
    via_rare = "npm:zzz-via-rare"
    tables = deepcopy(TABLES)
    tables["packages"] = [
        _pkg(seed),
        _pkg(via_popular),
        _pkg(via_rare),
        *[_pkg(f"npm:dummy-{i}") for i in range(20)],
    ]
    tables["maintainers"] = [_maint(popular), _maint(rare)]
    tables["edges_maintains"] = [
        {"mid": popular, "pid": seed},
        {"mid": popular, "pid": via_popular},
        *[{"mid": popular, "pid": f"npm:dummy-{i}"} for i in range(20)],
        {"mid": rare, "pid": seed},
        {"mid": rare, "pid": via_rare},
    ]
    cat = Catalog.from_tables(tables, ioc_records=[{"pid": seed, "split": "seed", "first_seen_utc": WORM}])

    def run(cypher: str, params: dict):
        if params["sourceNode"] != hydra_id(seed):
            return []
        return [
            FakePath(
                [_node(seed, "Package"), _node(popular, "Maintainer"), _node(via_popular, "Package")],
                [FakeRel("MAINTAINS"), FakeRel("MAINTAINS")],
            ),
            FakePath(
                [_node(seed, "Package"), _node(rare, "Maintainer"), _node(via_rare, "Package")],
                [FakeRel("MAINTAINS"), FakeRel("MAINTAINS")],
            ),
        ]

    engine = Engine(catalog=cat, run_paths=run)
    body = engine.forecast(
        seeds=[seed],
        as_of=WORM + 360,
        k=10,
        topology="trust",
        max_hops=3,
        limit=50,
        rank="popularity",
    )
    ranked = [row["pid"] for row in body["predictions"]]
    assert ranked[0] == via_popular
    assert body["stats"]["rank"] == "popularity"


def test_forecast_oidc_workflow_path_beats_plain_maintains():
    """Vector is 2 when the path includes a pull_request_target / OIDC workflow."""
    seed = "npm:seed-pkg"
    mid = "npm:aaa-maintainer"
    wid = "github:acme/app:.github/workflows/publish.yml"
    via_maint = "npm:aaa-via-maintains"
    via_oidc = "npm:zzz-via-oidc"
    tables = deepcopy(TABLES)
    tables["packages"] = [_pkg(seed), _pkg(via_maint), _pkg(via_oidc)]
    tables["maintainers"] = [_maint(mid)]
    tables["workflows"] = [
        {
            "wid": wid,
            "rid": "github:acme/app",
            "path": ".github/workflows/publish.yml",
            "trigger": "pull_request_target",
            "uses_pull_request_target": True,
            "has_oidc_publish": True,
        }
    ]
    tables["edges_maintains"] = [
        {"mid": mid, "pid": seed},
        {"mid": mid, "pid": via_maint},
    ]
    tables["edges_publishes_via_oidc"] = [{"wid": wid, "pid": via_oidc}]
    cat = Catalog.from_tables(
        tables,
        ioc_records=[{"pid": seed, "split": "seed", "first_seen_utc": WORM}],
    )

    def run(cypher: str, params: dict):
        if params["sourceNode"] != hydra_id(seed):
            return []
        return [
            FakePath(
                [_node(seed, "Package"), _node(mid, "Maintainer"), _node(via_maint, "Package")],
                [FakeRel("MAINTAINS"), FakeRel("MAINTAINS")],
            ),
            FakePath(
                [_node(seed, "Package"), _node(wid, "Workflow"), _node(via_oidc, "Package")],
                [FakeRel("PUBLISHES_VIA_OIDC"), FakeRel("PUBLISHES_VIA_OIDC")],
            ),
        ]

    engine = Engine(catalog=cat, run_paths=run)
    body = engine.forecast(seeds=[seed], as_of=WORM + 360, k=10, topology="trust", max_hops=3, limit=50)
    assert body["predictions"][0]["pid"] == via_oidc
    assert body["predictions"][1]["pid"] == via_maint
    assert body["predictions"][0]["score"] > body["predictions"][1]["score"]


def test_index_case_rare_maintainer_outranks_popular_at_the_same_coverage():
    observed = "npm:seed-pkg"
    popular = "npm:aaa-popular"
    rare = "npm:zzz-rare"
    tables = deepcopy(TABLES)
    tables["packages"] = [_pkg(observed), *[_pkg(f"npm:dummy-{i}") for i in range(20)]]
    tables["maintainers"] = [_maint(popular), _maint(rare)]
    tables["edges_maintains"] = [
        {"mid": popular, "pid": observed},
        *[{"mid": popular, "pid": f"npm:dummy-{i}"} for i in range(20)],
        {"mid": rare, "pid": observed},
        {"mid": rare, "pid": "npm:dummy-0"},
    ]
    cat = Catalog.from_tables(
        tables,
        ioc_records=[{"pid": observed, "split": "seed", "first_seen_utc": WORM}],
    )

    def run(cypher: str, params: dict):
        if params["sourceNode"] != hydra_id(observed):
            return []
        return [
            FakePath(
                [_node(observed, "Package"), _node(popular, "Maintainer")],
                [FakeRel("MAINTAINS")],
            ),
            FakePath(
                [_node(observed, "Package"), _node(rare, "Maintainer")],
                [FakeRel("MAINTAINS")],
            ),
        ]

    engine = Engine(catalog=cat, run_paths=run)
    body = engine.index_case(observed=[observed], as_of=WORM + 360, k=5, max_hops=4, limit=50)
    assert body["candidates"][0]["id"] == rare
    assert body["candidates"][1]["id"] == popular
    assert body["candidates"][0]["score"] > body["candidates"][1]["score"]


def test_forecast_repeat_hits_cache_and_does_not_reissue_sspaths():
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    seed = "npm:@tanstack/react-query"
    neighbour = "npm:@tanstack/store"
    mid = "npm:tannerlinsley"
    path = FakePath(
        [_node(seed, "Package"), _node(mid, "Maintainer"), _node(neighbour, "Package")],
        [FakeRel("MAINTAINS"), FakeRel("MAINTAINS")],
    )
    calls = {"n": 0}

    def run(cypher: str, params: dict):
        calls["n"] += 1
        return [path] if params["sourceNode"] == hydra_id(seed) else []

    engine = Engine(catalog=cat, run_paths=run)
    kwargs = dict(seeds=[seed], as_of=WORM + 360, k=10, topology="trust", max_hops=3, limit=50)
    first = engine.forecast(**kwargs)
    second = engine.forecast(**kwargs)
    assert first["predictions"][0]["pid"] == neighbour
    assert second["predictions"] == first["predictions"]
    assert calls["n"] == 1


def test_meta_default_blast_skips_seed_without_a_parquet_version():
    tables = deepcopy(TABLES)
    tables["packages"] = [
        _pkg("npm:@arktype/adapter"),
        _pkg("npm:@tanstack/react-query"),
    ]
    ioc = [
        {"pid": "npm:@arktype/adapter", "split": "seed", "first_seen_utc": WORM},
        {"pid": "npm:@tanstack/react-query", "split": "seed", "first_seen_utc": WORM},
    ]
    cat = Catalog.from_tables(tables, ioc_records=ioc)
    engine = Engine(catalog=cat, run_paths=lambda q, p: [])
    blast = engine.meta()["default_blast"]
    assert blast["name"] == "@tanstack/react-query"
    assert blast["version"] == "5.101.4"
    assert blast["ecosystem"] == "npm"


def test_meta_finding_vids_are_service_pins_in_the_ioc():
    tables = deepcopy(TABLES)
    ioc = [
        {
            "pid": "npm:@tanstack/react-query",
            "vid": "npm:@tanstack/react-query@5.101.4",
            "split": "seed",
            "first_seen_utc": WORM,
        },
        {
            "pid": "npm:lodash",
            "vid": "npm:lodash@4.17.21",
            "split": "validation",
            "first_seen_utc": WORM + 2000,
        },
    ]
    cat = Catalog.from_tables(tables, ioc_records=ioc)
    meta = Engine(catalog=cat, run_paths=lambda q, p: []).meta()
    assert meta["default_sid"] == "svc:app"
    assert meta["finding_vids"] == [{"vid": "npm:lodash@4.17.21", "at": WORM + 2000}]


def test_meta_prefers_mattermost_when_that_service_exists():
    tables = deepcopy(TABLES)
    tables["services"] = [
        {"sid": "svc:appwrite", "name": "appwrite", "source_repo": "github:appwrite/appwrite"},
        {"sid": "svc:mattermost", "name": "mattermost", "source_repo": "github:mattermost/mattermost"},
    ]
    cat = Catalog.from_tables(tables, ioc_records=IOC)
    assert Engine(catalog=cat, run_paths=lambda q, p: []).meta()["default_sid"] == "svc:mattermost"


def test_forecast_explicit_empty_seeds_does_not_fall_back_to_catalog():
    """UI sends [] before 19:26. That must not fan out the 42 IOC seeds."""
    calls = {"n": 0}

    def run(cypher: str, params: dict):
        calls["n"] += 1
        return []

    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    engine = Engine(catalog=cat, run_paths=run)
    body = engine.forecast(seeds=[], as_of=WORM + 360, k=10, topology="trust", max_hops=3, limit=50)
    assert body["predictions"] == []
    assert body["stats"]["seeds"] == 0
    assert calls["n"] == 0


def test_forecast_none_seeds_uses_catalog_seed_pids():
    calls: list[int] = []

    def run(cypher: str, params: dict):
        calls.append(params["sourceNode"])
        return []

    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    engine = Engine(catalog=cat, run_paths=run)
    body = engine.forecast(seeds=None, as_of=WORM + 360, k=10, topology="trust", max_hops=3, limit=50)
    assert body["stats"]["seeds"] == 1
    assert calls == [hydra_id("npm:@tanstack/react-query")]


def test_index_case_explicit_empty_observed_does_not_query():
    calls = {"n": 0}
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    engine = Engine(catalog=cat, run_paths=lambda q, p: calls.__setitem__("n", calls["n"] + 1) or [])
    body = engine.index_case(observed=[], as_of=WORM + 360, k=5, max_hops=4, limit=50)
    assert body["candidates"] == []
    assert body["stats"]["observed"] == 0
    assert calls["n"] == 0


def test_index_case_repeat_hits_cache():
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    observed = "npm:@tanstack/react-query"
    mid = "npm:tannerlinsley"
    path = FakePath(
        [_node(observed, "Package"), _node(mid, "Maintainer")],
        [FakeRel("MAINTAINS")],
    )
    calls = {"n": 0}

    def run(cypher: str, params: dict):
        calls["n"] += 1
        return [path] if params["sourceNode"] == hydra_id(observed) else []

    engine = Engine(catalog=cat, run_paths=run)
    kwargs = dict(observed=[observed], as_of=WORM + 360, k=5, max_hops=4, limit=50)
    first = engine.index_case(**kwargs)
    second = engine.index_case(**kwargs)
    assert first["candidates"][0]["id"] == mid
    assert second["candidates"] == first["candidates"]
    assert calls["n"] == 1


def test_forecast_cache_return_is_a_copy():
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    engine = Engine(catalog=cat, run_paths=lambda q, p: [])
    first = engine.forecast(seeds=["npm:@tanstack/react-query"], as_of=WORM + 360, k=10, topology="trust", max_hops=3, limit=50)
    first["stub"] = True
    first["predictions"].append({"pid": "injected"})
    second = engine.forecast(seeds=["npm:@tanstack/react-query"], as_of=WORM + 360, k=10, topology="trust", max_hops=3, limit=50)
    assert "stub" not in second
    assert second["predictions"] == []


def test_sspaths_exception_returns_empty_predictions():
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)

    def boom(cypher: str, params: dict):
        raise RuntimeError("bolt down")

    engine = Engine(catalog=cat, run_paths=boom)
    body = engine.forecast(
        seeds=["npm:@tanstack/react-query"],
        as_of=WORM + 360,
        k=10,
        topology="trust",
        max_hops=3,
        limit=50,
    )
    assert body["predictions"] == []


def test_forecast_same_key_single_flights_across_threads():
    import threading
    import time

    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    entered = threading.Event()
    release = threading.Event()
    calls = {"n": 0}

    def run(cypher: str, params: dict):
        calls["n"] += 1
        entered.set()
        assert release.wait(timeout=2)
        return []

    engine = Engine(catalog=cat, run_paths=run)
    kwargs = dict(
        seeds=["npm:@tanstack/react-query"],
        as_of=WORM + 360,
        k=10,
        topology="trust",
        max_hops=3,
        limit=50,
    )
    results: list[dict] = []

    def call():
        results.append(engine.forecast(**kwargs))

    first = threading.Thread(target=call)
    second = threading.Thread(target=call)
    first.start()
    assert entered.wait(timeout=2)
    second.start()
    time.sleep(0.1)
    assert calls["n"] == 1
    release.set()
    first.join(timeout=2)
    second.join(timeout=2)
    assert first.is_alive() is False
    assert second.is_alive() is False
    assert calls["n"] == 1
    assert len(results) == 2
    assert results[0]["predictions"] == results[1]["predictions"] == []


def test_forecast_two_sources_merge_in_source_order():
    seed_a = "npm:seed-a"
    seed_b = "npm:seed-b"
    cand_a = "npm:cand-a"
    cand_b = "npm:cand-b"
    mid = "npm:shared"
    tables = deepcopy(TABLES)
    tables["packages"] = [_pkg(seed_a), _pkg(seed_b), _pkg(cand_a), _pkg(cand_b)]
    tables["maintainers"] = [_maint(mid)]
    tables["edges_maintains"] = [
        {"mid": mid, "pid": seed_a},
        {"mid": mid, "pid": seed_b},
        {"mid": mid, "pid": cand_a},
        {"mid": mid, "pid": cand_b},
    ]
    cat = Catalog.from_tables(
        tables,
        ioc_records=[
            {"pid": seed_a, "split": "seed", "first_seen_utc": WORM},
            {"pid": seed_b, "split": "seed", "first_seen_utc": WORM},
        ],
    )

    def run(cypher: str, params: dict):
        src = params["sourceNode"]
        if src == hydra_id(seed_a):
            return [
                FakePath(
                    [_node(seed_a, "Package"), _node(mid, "Maintainer"), _node(cand_a, "Package")],
                    [FakeRel("MAINTAINS"), FakeRel("MAINTAINS")],
                )
            ]
        if src == hydra_id(seed_b):
            return [
                FakePath(
                    [_node(seed_b, "Package"), _node(mid, "Maintainer"), _node(cand_b, "Package")],
                    [FakeRel("MAINTAINS"), FakeRel("MAINTAINS")],
                )
            ]
        return []

    engine = Engine(catalog=cat, run_paths=run)
    body = engine.forecast(
        seeds=[seed_a, seed_b],
        as_of=WORM + 360,
        k=10,
        topology="trust",
        max_hops=3,
        limit=50,
    )
    ranked = [row["pid"] for row in body["predictions"]]
    assert ranked == [cand_a, cand_b]


def test_index_case_same_key_single_flights_across_threads():
    import threading
    import time

    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    entered = threading.Event()
    release = threading.Event()
    calls = {"n": 0}

    def run(cypher: str, params: dict):
        calls["n"] += 1
        entered.set()
        assert release.wait(timeout=2)
        return []

    engine = Engine(catalog=cat, run_paths=run)
    kwargs = dict(observed=["npm:@tanstack/react-query"], as_of=WORM + 360, k=5, max_hops=4, limit=50)
    results: list[dict] = []

    def call():
        results.append(engine.index_case(**kwargs))

    first = threading.Thread(target=call)
    second = threading.Thread(target=call)
    first.start()
    assert entered.wait(timeout=2)
    second.start()
    time.sleep(0.1)
    assert calls["n"] == 1
    release.set()
    first.join(timeout=2)
    second.join(timeout=2)
    assert calls["n"] == 1
    assert len(results) == 2
