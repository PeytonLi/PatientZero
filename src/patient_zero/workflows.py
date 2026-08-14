"""Flag GitHub Actions workflows for the actual worm vector."""

from __future__ import annotations

import re

from patient_zero.ids import wid

_PRT = re.compile(r"(?m)^\s*pull_request_target\s*:")
_PR = re.compile(r"(?m)^\s*pull_request\s*:")
_OIDC = re.compile(r"(?m)^\s*id-token:\s*write\s*$")


def parse_workflow(*, rid: str, path: str, yaml_text: str) -> dict:
    uses_prt = bool(_PRT.search(yaml_text))
    if uses_prt:
        trigger = "pull_request_target"
    elif _PR.search(yaml_text):
        trigger = "pull_request"
    else:
        trigger = "other"
    return {
        "wid": wid(rid, path),
        "rid": rid,
        "path": path,
        "trigger": trigger,
        "uses_pull_request_target": uses_prt,
        "has_oidc_publish": bool(_OIDC.search(yaml_text)),
    }
