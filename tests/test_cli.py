"""CLI: python -m patient_zero.etl or scripts/etl.py."""

from pathlib import Path

from patient_zero.cli import main


def test_cli_offline_writes_manifest(tmp_path: Path):
    ioc = tmp_path / "ioc.json"
    packs = tmp_path / "packuments.json"
    out = tmp_path / "graph"
    ioc.write_text(
        '{"records":[{"pid":"npm:left-pad","vid":"npm:left-pad@1.3.0","ecosystem":"npm","split":"seed"}]}',
        encoding="utf-8",
    )
    packs.write_text(
        '[{"pid":"npm:left-pad","vid":"npm:left-pad@1.3.0","has_install_script":false,"install_hooks":[],"maintainer_logins":[],"repo_url":null,"published_at":1}]',
        encoding="utf-8",
    )
    rc = main(
        [
            "--offline",
            "--ioc",
            str(ioc),
            "--packuments",
            str(packs),
            "--out",
            str(out),
        ]
    )
def test_collect_logins_skips_pypi_and_dedupes():
    from patient_zero.cli import collect_logins

    logins = collect_logins(
        [
            {"pid": "npm:a", "maintainer_logins": ["tannerlinsley", "tkdodo"]},
            {"pid": "npm:b", "maintainer_logins": ["tannerlinsley"]},
            {"pid": "pypi:mistralai", "maintainer_logins": ["Mistral"]},
        ]
    )
    assert logins == ["tannerlinsley", "tkdodo"]
