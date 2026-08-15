"""Parquet catalog: HydraDB nodes are {id} plus a label; names live here."""

from patient_zero.catalog import Catalog
from patient_zero.ids import hydra_id, vid

WORM = 1778527200
SENTINEL = 4102444800

TABLES = {
    "packages": [
        {"pid": "npm:@tanstack/react-query", "ecosystem": "npm", "name": "@tanstack/react-query"},
        {"pid": "npm:@tanstack/store", "ecosystem": "npm", "name": "@tanstack/store"},
    ],
    "versions": [
        {
            "vid": "npm:@tanstack/react-query@5.101.4",
            "pid": "npm:@tanstack/react-query",
            "ecosystem": "npm",
            "name": "@tanstack/react-query",
            "version": "5.101.4",
            "published_at": WORM,
            "unpublished_at": None,
            "has_install_script": False,
            "install_hooks": [],
        },
        {
            "vid": "npm:lodash@4.17.21",
            "pid": "npm:lodash",
            "ecosystem": "npm",
            "name": "lodash",
            "version": "4.17.21",
            "published_at": 1,
            "unpublished_at": None,
            "has_install_script": True,
            "install_hooks": ["postinstall"],
        },
    ],
    "maintainers": [
        {
            "mid": "npm:tannerlinsley",
            "ecosystem": "npm",
            "login": "tannerlinsley",
            "email_domain": None,
            "twofa": None,
        }
    ],
    "repos": [
        {"rid": "github:TanStack/query", "host": "github", "org": "TanStack", "name": "query"}
    ],
    "workflows": [
        {
            "wid": "github:TanStack/query:.github/workflows/release.yml",
            "rid": "github:TanStack/query",
            "path": ".github/workflows/release.yml",
            "trigger": "pull_request_target",
            "uses_pull_request_target": True,
            "has_oidc_publish": True,
        }
    ],
    "services": [{"sid": "svc:app", "name": "app", "source_repo": "github:acme/app"}],
    "advisories": [],
    "edges_depends_on": [],
    "edges_pins": [
        {
            "sid": "svc:app",
            "dst_vid": "npm:lodash@4.17.21",
            "lockfile_at": WORM + 100,
            "valid_from": WORM + 100,
            "valid_to": SENTINEL,
        }
    ],
    "edges_maintains": [
        {"mid": "npm:tannerlinsley", "pid": "npm:@tanstack/react-query"},
        {"mid": "npm:tannerlinsley", "pid": "npm:@tanstack/store"},
    ],
    "edges_published_from": [{"pid": "npm:@tanstack/react-query", "rid": "github:TanStack/query"}],
    "edges_has_workflow": [
        {"rid": "github:TanStack/query", "wid": "github:TanStack/query:.github/workflows/release.yml"}
    ],
    "edges_publishes_via_oidc": [
        {
            "wid": "github:TanStack/query:.github/workflows/release.yml",
            "pid": "npm:@tanstack/react-query",
        }
    ],
    "edges_affects": [],
}

IOC = [
    {
        "pid": "npm:@tanstack/react-query",
        "vid": "npm:@tanstack/react-query@5.90.2",
        "split": "seed",
        "first_seen_utc": WORM,
    },
    {
        "pid": "npm:@tanstack/store",
        "vid": "npm:@tanstack/store@0.7.0",
        "split": "validation",
        "first_seen_utc": WORM + 2000,
    },
]


def test_catalog_maps_hydra_id_back_to_stable_and_label():
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    hid = hydra_id("npm:@tanstack/react-query")
    rec = cat.by_hydra[hid]
    assert rec.stable == "npm:@tanstack/react-query"
    assert rec.label == "Package"
    assert cat.stable(hid) == "npm:@tanstack/react-query"


def test_catalog_resolves_missing_version_to_the_loaded_vid():
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    exact = vid("npm", "@tanstack/react-query", "5.0.1")
    assert exact not in {row["vid"] for row in TABLES["versions"]}
    assert cat.resolve_vid("npm", "@tanstack/react-query", "5.0.1") == (
        "npm:@tanstack/react-query@5.101.4"
    )


def test_catalog_seed_and_validation_pids_from_ioc_split():
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    assert cat.seed_pids == frozenset({"npm:@tanstack/react-query"})
    assert cat.validation_pids == frozenset({"npm:@tanstack/store"})


def test_catalog_degree_counts_maintainers_repos_and_workflows():
    cat = Catalog.from_tables(TABLES, ioc_records=IOC)
    assert cat.degree("npm:tannerlinsley") == 2
    assert cat.degree("github:TanStack/query") == 1
    assert cat.degree("github:TanStack/query:.github/workflows/release.yml") == 1
    assert cat.degree("npm:unknown-entity") == 1
