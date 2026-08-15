"""Repo-relative paths for editable installs and Docker."""

from patient_zero.paths import graph_dir, ioc_path, repo_root


def test_repo_root_finds_artifacts():
    root = repo_root()
    assert (root / "artifacts" / "ioc.json").is_file()
    assert (root / "pyproject.toml").is_file()


def test_default_paths_are_under_root():
    root = repo_root()
    assert ioc_path() == root / "artifacts" / "ioc.json"
    assert graph_dir() == root / "data" / "graph"
    assert ioc_path().is_file()
