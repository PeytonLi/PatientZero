"""May 11 is fixture #1, loaded from JSON, not a pile of engine constants."""

from patient_zero.incident import TRUE_ORIGIN_MID, WORM_START, Incident


def test_may11_matches_baked_clock():
    incident = Incident.may11()
    assert incident.id == "may11-tanstack"
    assert incident.window_start == WORM_START == 1778527200
    assert incident.named_at == WORM_START + 360
    assert incident.world_found_out_at == WORM_START + 1560
    assert incident.true_origin_id == TRUE_ORIGIN_MID
    assert incident.ticks[0].label == "worm begins"
    assert incident.as_dict()["true_origin"]["kind"] == "maintainer"


def test_from_env_honors_path(tmp_path, monkeypatch):
    path = tmp_path / "other.json"
    path.write_text(
        """
        {
          "id": "other",
          "title": "Other",
          "window_start": 1,
          "window_end": 2,
          "named_at": 1,
          "world_found_out_at": 2,
          "true_origin": {"id": "npm:x", "kind": "maintainer"},
          "default_blast": {"ecosystem": "npm", "name": "x", "version": "1"},
          "default_sid": "svc:x",
          "ticks": [{"at": 1, "label": "start"}]
        }
        """,
        encoding="utf-8",
    )
    monkeypatch.setenv("PATIENT_ZERO_INCIDENT", str(path))
    loaded = Incident.from_env()
    assert loaded.id == "other"
    assert loaded.window_end == 2
