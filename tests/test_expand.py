"""Maintainer expansion. Forecast dies if we only keep already-compromised packages."""

from patient_zero.assemble import is_human_login
from patient_zero.expand import packages_from_search


SEARCH = {
    "objects": [
        {"package": {"name": "@tanstack/query-core"}},
        {"package": {"name": "@tanstack/react-query"}},
        {"package": {"name": "left-pad"}},
    ]
}


def test_packages_from_search_emits_pids_for_human_maintainer():
    rows = packages_from_search(SEARCH, login="tannerlinsley", ecosystem="npm")
    assert [r["pid"] for r in rows] == [
        "npm:@tanstack/query-core",
        "npm:@tanstack/react-query",
        "npm:left-pad",
    ]
    assert all(r["mid"] == "npm:tannerlinsley" for r in rows)


def test_packages_from_search_empty_for_bot_login():
    assert packages_from_search(SEARCH, login="GitHub Actions", ecosystem="npm") == []
