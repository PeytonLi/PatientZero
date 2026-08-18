"""Identity home: if this credential is stolen, what falls?"""

from patient_zero.catalog import Catalog
from patient_zero.engine import Engine
from patient_zero.ids import hydra_id
from test_catalog import IOC, TABLES
from test_engine import FakePath, FakeRel, _node


def test_unknown_identity_is_not_found():
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    engine = Engine(catalog=cat, run_paths=lambda _q, _p: [])
    body = engine.identity(stable_id="npm:nobody")
    assert body["found"] is False
    assert body["id"] == "npm:nobody"
    assert body["packages"] == []


def test_maintainer_identity_lists_packages_they_maintain():
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    engine = Engine(catalog=cat, run_paths=lambda _q, _p: [])
    body = engine.identity(stable_id="npm:tannerlinsley")
    assert body["found"] is True
    assert body["kind"] == "maintainer"
    assert body["name"] == "tannerlinsley"
    pids = [row["pid"] for row in body["packages"]]
    assert pids == ["npm:@tanstack/react-query", "npm:@tanstack/store"]
    assert body["packages"][0]["ecosystem"] == "npm"
    assert body["registries"] == ["npm"]


def test_identity_names_mincut_action_when_credential_covers_neighborhood():
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    seed = "npm:@tanstack/react-query"
    neighbour = "npm:@tanstack/store"
    mid = "npm:tannerlinsley"
    path = FakePath(
        [_node(seed, "Package"), _node(mid, "Maintainer"), _node(neighbour, "Package")],
        [FakeRel("MAINTAINS"), FakeRel("MAINTAINS")],
    )

    def run(cypher: str, params: dict):
        if "MAINTAINS" in cypher and params["sourceNode"] == hydra_id(seed):
            return [path]
        return []

    engine = Engine(catalog=cat, run_paths=run)
    body = engine.identity(stable_id=mid)
    assert body["packages_at_risk"] == 1
    assert body["action"] == "revoke"
    assert neighbour in body["path"]


def test_workflow_identity_lists_packages_published_via_oidc():
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    engine = Engine(catalog=cat, run_paths=lambda _q, _p: [])
    wid = "github:TanStack/query:.github/workflows/release.yml"
    body = engine.identity(stable_id=wid)
    assert body["found"] is True
    assert body["kind"] == "workflow"
    assert body["packages"][0]["pid"] == "npm:@tanstack/react-query"
    assert body["action"] is None


def test_same_login_across_ecosystems_is_an_alias():
    from copy import deepcopy

    tables = deepcopy(TABLES)
    tables["maintainers"] = list(tables["maintainers"]) + [
        {
            "mid": "pypi:tannerlinsley",
            "ecosystem": "pypi",
            "login": "tannerlinsley",
            "email_domain": None,
            "twofa": None,
        }
    ]
    tables["packages"] = list(tables["packages"]) + [
        {"pid": "pypi:tanstack", "ecosystem": "pypi", "name": "tanstack"}
    ]
    tables["edges_maintains"] = list(tables["edges_maintains"]) + [
        {"mid": "pypi:tannerlinsley", "pid": "pypi:tanstack"}
    ]
    cat = Catalog.from_tables(tables, ioc_records=IOC)
    engine = Engine(catalog=cat, run_paths=lambda _q, _p: [])
    body = engine.identity(stable_id="npm:tannerlinsley")
    alias_ids = [row["id"] for row in body["aliases"]]
    assert "pypi:tannerlinsley" in alias_ids
    assert "npm" in body["registries"] and "pypi" in body["registries"]


def test_shared_email_domain_is_an_alias():
    from copy import deepcopy

    tables = deepcopy(TABLES)
    tables["maintainers"][0]["email_domain"] = "tanstack.com"
    tables["maintainers"] = list(tables["maintainers"]) + [
        {
            "mid": "pypi:tlinz",
            "ecosystem": "pypi",
            "login": "tlinz",
            "email_domain": "tanstack.com",
            "twofa": None,
        }
    ]
    cat = Catalog.from_tables(tables, ioc_records=IOC)
    engine = Engine(catalog=cat, run_paths=lambda _q, _p: [])
    body = engine.identity(stable_id="npm:tannerlinsley")
    assert "pypi:tlinz" in [row["id"] for row in body["aliases"]]


def test_shared_github_org_adds_the_other_registry():
    from copy import deepcopy

    tables = deepcopy(TABLES)
    tables["packages"] = list(tables["packages"]) + [
        {"pid": "pypi:tanstack", "ecosystem": "pypi", "name": "tanstack"}
    ]
    tables["edges_published_from"] = list(tables["edges_published_from"]) + [
        {"pid": "pypi:tanstack", "rid": "github:TanStack/query"}
    ]
    cat = Catalog.from_tables(tables, ioc_records=IOC)
    engine = Engine(catalog=cat, run_paths=lambda _q, _p: [])
    body = engine.identity(stable_id="npm:tannerlinsley")
    assert "pypi" in body["registries"]
