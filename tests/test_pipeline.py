"""Full graph build from in-memory inputs. Network stays out of the unit tests."""

from patient_zero.assemble import SENTINEL_VALID_TO
from patient_zero.pipeline import build_graph


def test_build_graph_wires_trust_dependency_pins_and_advisory():
    ioc = [
        {
            "pid": "npm:@tanstack/react-query",
            "vid": "npm:@tanstack/react-query@5.90.2",
            "ecosystem": "npm",
            "split": "seed",
        }
    ]
    packuments = [
        {
            "pid": "npm:@tanstack/react-query",
            "vid": "npm:@tanstack/react-query@5.90.2",
            "has_install_script": False,
            "install_hooks": [],
            "maintainer_logins": ["tannerlinsley"],
            "repo_url": "github:TanStack/query",
            "published_at": 100,
        }
    ]
    dep_graphs = {
        "npm:@tanstack/react-query@5.90.2": {
            "nodes": [
                {
                    "versionKey": {
                        "system": "NPM",
                        "name": "@tanstack/react-query",
                        "version": "5.90.2",
                    }
                },
                {
                    "versionKey": {
                        "system": "NPM",
                        "name": "@tanstack/query-core",
                        "version": "5.90.2",
                    }
                },
            ],
            "edges": [{"fromNode": 0, "toNode": 1, "requirement": "5.90.2"}],
        }
    }
    searches = {
        "tannerlinsley": {
            "objects": [{"package": {"name": "@tanstack/store"}}]
        }
    }
    tables = build_graph(
        ioc_records=ioc,
        packuments=packuments,
        dep_graphs=dep_graphs,
        searches=searches,
        services=[{"sid": "svc:app", "name": "app", "source_repo": "github:acme/app"}],
        pins=[
            {
                "sid": "svc:app",
                "dst_vid": "npm:@tanstack/react-query@5.90.2",
                "lockfile_at": 50,
                "valid_from": 50,
                "valid_to": SENTINEL_VALID_TO,
            }
        ],
        workflows=[
            {
                "wid": "github:TanStack/query:.github/workflows/release.yml",
                "rid": "github:TanStack/query",
                "path": ".github/workflows/release.yml",
                "trigger": "pull_request_target",
                "uses_pull_request_target": True,
                "has_oidc_publish": True,
            }
        ],
    )
    pids = {r["pid"] for r in tables["packages"]}
    assert "npm:@tanstack/store" in pids
    assert "npm:@tanstack/query-core" in pids
    assert any(
        r["mid"] == "npm:tannerlinsley" and r["pid"] == "npm:@tanstack/store"
        for r in tables["edges_maintains"]
    )
    assert tables["edges_depends_on"][0]["dst_vid"] == "npm:@tanstack/query-core@5.90.2"
    assert tables["services"][0]["sid"] == "svc:app"
    assert tables["edges_pins"][0]["dst_vid"] == "npm:@tanstack/react-query@5.90.2"
    assert tables["workflows"][0]["uses_pull_request_target"] is True
    assert tables["edges_has_workflow"][0]["rid"] == "github:TanStack/query"
    assert tables["edges_has_workflow"][0]["wid"] == (
        "github:TanStack/query:.github/workflows/release.yml"
    )
    assert tables["edges_has_workflow"][0]["valid_from"] == 0
    assert tables["edges_has_workflow"][0]["valid_to"] == SENTINEL_VALID_TO
    assert tables["edges_publishes_via_oidc"][0]["wid"] == (
        "github:TanStack/query:.github/workflows/release.yml"
    )
    assert tables["edges_publishes_via_oidc"][0]["pid"] == "npm:@tanstack/react-query"
    assert tables["edges_publishes_via_oidc"][0]["valid_from"] == 0
    assert tables["advisories"][0]["aid"] == "ghsa:GHSA-g7cv-rxg3-hmpx"
    assert any(r["vid"] == "npm:@tanstack/react-query@5.90.2" for r in tables["edges_affects"])
