"""Accepted Cypher shapes. HydraDB 0.1.0 SSpaths is not the README map."""

from patient_zero.cypher import ss_paths


def test_ss_paths_binds_integer_sourceNode_not_vid_property():
    query = ss_paths(
        rel_types=["DEPENDS_ON", "PINS"],
        direction="incoming",
        max_len=6,
        path_count=50,
        result_limit=50,
    )
    assert "sourceNode: $sourceNode" in query
    assert "sourceProperty" not in query
    assert "'vid'" not in query
    assert "'pid'" not in query
    assert "maxLen: 6" in query
    assert "pathCount: 50" in query
    assert "resultLimit: 50" in query
    assert "YIELD path" in query
    assert "relTypes: ['DEPENDS_ON', 'PINS']" in query
    assert "relDirection: 'incoming'" in query
    assert "CALL algo.SSpaths" in query


def test_ss_paths_rejects_zero_path_count():
    import pytest

    with pytest.raises(ValueError, match="pathCount"):
        ss_paths(
            rel_types=["MAINTAINS"],
            direction="both",
            max_len=3,
            path_count=0,
            result_limit=10,
        )
