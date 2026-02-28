"""Unit tests for interaction filtering logic."""

from app.models.interaction import InteractionLog
from app.routers.interactions import _filter_by_item_id


def _make_log(id: int, learner_id: int, item_id: int) -> InteractionLog:
    return InteractionLog(id=id, learner_id=learner_id, item_id=item_id, kind="attempt")


def test_filter_returns_all_when_item_id_is_none() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, None)
    assert result == interactions


def test_filter_returns_empty_for_empty_input() -> None:
    result = _filter_by_item_id([], 1)
    assert result == []


def test_filter_returns_interaction_with_matching_ids() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 1
    assert result[0].id == 1


def test_filter_excludes_interaction_with_different_learner_id() -> None:
    """Test that filtering by item_id includes interactions even when learner_id differs."""
    interactions = [_make_log(1, 2, 1)]  # id=1, learner_id=2, item_id=1
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 1
    assert result[0].id == 1
    assert result[0].learner_id == 2
    assert result[0].item_id == 1


def test_filter_returns_all_matches_when_multiple_interactions_share_same_item_id() -> None:
    """Test that filtering returns all interactions with matching item_id, not just the first."""
    interactions = [
        _make_log(1, 1, 5),
        _make_log(2, 2, 5),
        _make_log(3, 3, 5),
        _make_log(4, 1, 7),
    ]
    result = _filter_by_item_id(interactions, 5)
    assert len(result) == 3
    assert all(i.item_id == 5 for i in result)
    assert {i.id for i in result} == {1, 2, 3}


def test_filter_with_zero_item_id_returns_empty() -> None:
    """Test boundary case: filtering by item_id=0 returns no results when no interactions have id 0."""
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, 0)
    assert result == []


def test_filter_with_large_item_id_boundary() -> None:
    """Test boundary case: filtering with large integer item_id works correctly."""
    large_id = 2**31 - 1  # Max 32-bit signed integer
    interactions = [
        _make_log(1, 1, 1),
        _make_log(2, 2, large_id),
    ]
    result = _filter_by_item_id(interactions, large_id)
    assert len(result) == 1
    assert result[0].item_id == large_id


def test_filter_with_negative_item_id_returns_empty() -> None:
    """Test boundary case: filtering by negative item_id returns no results."""
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, -1)
    assert result == []
