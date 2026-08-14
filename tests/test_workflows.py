"""Workflow vector flags. Missing pull_request_target would miss the actual breach."""

from patient_zero.workflows import parse_workflow

PWN = """
name: release
on:
  pull_request_target:
    types: [opened]
permissions:
  id-token: write
  contents: read
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
"""

SAFE = """
name: ci
on:
  pull_request:
    branches: [main]
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: npm test
"""


def test_parse_workflow_flags_pwn_request_and_oidc():
    row = parse_workflow(
        rid="github:TanStack/query",
        path=".github/workflows/release.yml",
        yaml_text=PWN,
    )
    assert row["wid"] == "github:TanStack/query:.github/workflows/release.yml"
    assert row["trigger"] == "pull_request_target"
    assert row["uses_pull_request_target"] is True
    assert row["has_oidc_publish"] is True


def test_parse_workflow_safe_pr_is_not_the_vector():
    row = parse_workflow(
        rid="github:TanStack/query",
        path=".github/workflows/ci.yml",
        yaml_text=SAFE,
    )
    assert row["uses_pull_request_target"] is False
    assert row["has_oidc_publish"] is False
    assert row["trigger"] == "pull_request"
