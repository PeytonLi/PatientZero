"""Stable graph IDs. A wrong prefix or leftover .git would silently duplicate nodes."""

from patient_zero.ids import mid, pid, rid, vid, wid


def test_pid_scopes_ecosystem_and_name():
    assert pid("npm", "@tanstack/react-query") == "npm:@tanstack/react-query"
    assert pid("pypi", "mistralai") == "pypi:mistralai"


def test_vid_appends_version_without_doubling_at():
    assert (
        vid("npm", "@tanstack/react-query", "5.0.1")
        == "npm:@tanstack/react-query@5.0.1"
    )


def test_mid_is_ecosystem_login():
    assert mid("npm", "tannerlinsley") == "npm:tannerlinsley"


def test_rid_normalizes_github_urls_to_host_org_name():
    assert rid("https://github.com/TanStack/query") == "github:TanStack/query"
    assert rid("https://github.com/TanStack/query.git") == "github:TanStack/query"
    assert rid("git+ssh://git@github.com/TanStack/query.git") == "github:TanStack/query"
    assert rid("github:TanStack/query") == "github:TanStack/query"


def test_rid_returns_none_when_not_github():
    assert rid("https://gitlab.com/foo/bar") is None
    assert rid("") is None
    assert rid(None) is None


def test_wid_joins_repo_and_workflow_path():
    assert (
        wid("github:TanStack/query", ".github/workflows/publish.yml")
        == "github:TanStack/query:.github/workflows/publish.yml"
    )


def test_hydra_id_is_stable_non_negative_int():
    from patient_zero.ids import hydra_id

    a = hydra_id("npm:@tanstack/query-core@5.90.2")
    b = hydra_id("npm:@tanstack/query-core@5.90.2")
    c = hydra_id("npm:@tanstack/react-query@5.90.2")
    assert a == b
    assert isinstance(a, int)
    assert a >= 0
    assert c >= 0
    assert a != c
    assert a <= 0x7FFFFFFFFFFFFFFF
