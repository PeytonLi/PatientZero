"""Repo-relative data paths that work from an editable install and from Docker."""

from __future__ import annotations

import os
from pathlib import Path

LOAD_SENTINEL_PID = "npm:@tanstack/react-query"


def repo_root() -> Path:
    env = os.environ.get("PATIENT_ZERO_ROOT")
    if env:
        return Path(env)
    here = Path(__file__).resolve()
    candidates = [here.parents[2], Path.cwd()]
    for candidate in candidates:
        if (candidate / "artifacts" / "ioc.json").is_file():
            return candidate
        if (candidate / "data" / "graph").is_dir():
            return candidate
    return Path.cwd()


def graph_dir() -> Path:
    env = os.environ.get("PATIENT_ZERO_GRAPH_DIR")
    if env:
        return Path(env)
    return repo_root() / "data" / "graph"


def ioc_path() -> Path:
    env = os.environ.get("PATIENT_ZERO_IOC_PATH")
    if env:
        return Path(env)
    return repo_root() / "artifacts" / "ioc.json"
