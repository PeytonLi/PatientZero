"""IOC + packument join. Duplicates become duplicate HydraDB nodes; bots are supernodes."""

from patient_zero.assemble import SENTINEL_VALID_TO, assemble
from patient_zero.ids import mid, pid, rid, vid

IOC = [
    {
        "pid": "npm:@tanstack/query-core",
        "vid": "npm:@tanstack/query-core@5.90.2",
        "ecosystem": "npm",
        "first_seen_utc": 1778527200,
        "sources": ["https://tanstack.com/blog/npm-supply-chain-compromise-postmortem"],
        "confidence": 1.0,
        "split": "seed",
    },
    {
        "pid": "npm:@tanstack/query-core",
        "vid": "npm:@tanstack/query-core@5.90.2",
        "ecosystem": "npm",
        "first_seen_utc": 1778527200,
        "sources": ["https://www.wiz.io/blog/mini-shai-hulud-strikes-again-tanstack-more-npm-packages-compromised"],
        "confidence": 0.9,
        "split": "seed",
    },
    {
        "pid": "pypi:mistralai",
        "vid": "pypi:mistralai@1.7.1",
        "ecosystem": "pypi",
        "first_seen_utc": 1778530000,
        "sources": ["https://safedep.io/mass-npm-supply-chain-attack-tanstack-mistral"],
        "confidence": 0.8,
        "split": "validation",
    },
]

PACKUMENTS = [
    {
        "pid": "npm:@tanstack/query-core",
        "vid": "npm:@tanstack/query-core@5.90.2",
        "has_install_script": False,
        "install_hooks": [],
        "maintainer_logins": ["GitHub Actions", "tannerlinsley", "tkdodo"],
        "repo_url": "github:TanStack/query",
        "published_at": 1778527239,
    },
]


def test_sentinel_valid_to_is_year_2100_not_null():
    assert SENTINEL_VALID_TO == 4102444800


def test_assemble_dedupes_packages_and_versions_by_stable_id():
    g = assemble(IOC, PACKUMENTS)
    assert [row["pid"] for row in g["packages"]] == [
        "npm:@tanstack/query-core",
        "pypi:mistralai",
    ]
    assert [row["vid"] for row in g["versions"]] == [
        "npm:@tanstack/query-core@5.90.2",
        "pypi:mistralai@1.7.1",
    ]


def test_assemble_drops_bot_maintainers_and_links_humans():
    g = assemble(IOC, PACKUMENTS)
    logins = [row["login"] for row in g["maintainers"]]
    assert "GitHub Actions" not in logins
    assert logins == ["tannerlinsley", "tkdodo"]
    assert g["edges_maintains"] == [
        {
            "mid": mid("npm", "tannerlinsley"),
            "pid": pid("npm", "@tanstack/query-core"),
            "valid_from": 0,
            "valid_to": SENTINEL_VALID_TO,
        },
        {
            "mid": mid("npm", "tkdodo"),
            "pid": pid("npm", "@tanstack/query-core"),
            "valid_from": 0,
            "valid_to": SENTINEL_VALID_TO,
        },
    ]


def test_assemble_joins_packument_hooks_and_repo():
    g = assemble(IOC, PACKUMENTS)
    version = g["versions"][0]
    assert version["has_install_script"] is False
    assert version["install_hooks"] == []
    assert version["published_at"] == 1778527239
    assert g["repos"] == [{"rid": "github:TanStack/query", "host": "github", "org": "TanStack", "name": "query"}]
    assert g["edges_published_from"] == [
        {
            "pid": "npm:@tanstack/query-core",
            "rid": "github:TanStack/query",
            "valid_from": 0,
            "valid_to": SENTINEL_VALID_TO,
        }
    ]


def test_assemble_sorts_deterministically():
    reversed_ioc = list(reversed(IOC))
    g1 = assemble(IOC, PACKUMENTS)
    g2 = assemble(reversed_ioc, PACKUMENTS)
    assert g1["packages"] == g2["packages"]
    assert g1["versions"] == g2["versions"]
    assert g1["edges_maintains"] == g2["edges_maintains"]
