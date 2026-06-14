import pytest
from state_machine import StateMachine


def test_transition_accepted():
    sm = StateMachine(initial="draft")
    sm.transition("submit", from_state="draft", to_state="submitted")
    result = sm.send("submit", {})
    assert result.accepted is True
    assert result.to_state == "submitted"
    assert sm.current_state == "submitted"


def test_transition_rejected_wrong_state():
    sm = StateMachine(initial="processing")
    sm.transition("submit", from_state="draft", to_state="submitted")
    result = sm.send("submit", {})
    assert result.accepted is False
    assert sm.current_state == "processing"


def test_guard_passes():
    sm = StateMachine(initial="draft")
    sm.transition("submit", from_state="draft", to_state="submitted", guard="score > 50")
    result = sm.send("submit", {"score": 80})
    assert result.accepted is True
    assert sm.current_state == "submitted"


def test_guard_fails_state_unchanged():
    sm = StateMachine(initial="draft")
    sm.transition("submit", from_state="draft", to_state="submitted", guard="score > 50")
    result = sm.send("submit", {"score": 20})
    assert result.accepted is False
    assert sm.current_state == "draft"


def test_guard_compound():
    sm = StateMachine(initial="draft")
    sm.transition(
        "submit",
        from_state="draft",
        to_state="submitted",
        guard='order.total > 0 AND customer.verified == true',
    )
    ctx = {"order": {"total": 150}, "customer": {"verified": True}}
    assert sm.send("submit", ctx).accepted is True

    sm.reset()
    ctx["customer"]["verified"] = False
    assert sm.send("submit", ctx).accepted is False


def test_multi_source_from_state():
    sm = StateMachine(initial="submitted")
    sm.transition("cancel", from_state=["draft", "submitted", "processing"], to_state="cancelled")
    result = sm.send("cancel", {})
    assert result.accepted is True
    assert sm.current_state == "cancelled"


def test_multi_source_wrong_state():
    sm = StateMachine(initial="delivered")
    sm.transition("cancel", from_state=["draft", "submitted", "processing"], to_state="cancelled")
    result = sm.send("cancel", {})
    assert result.accepted is False


def test_action_mutates_context():
    sm = StateMachine(initial="draft")
    sm.transition(
        "submit",
        from_state="draft",
        to_state="submitted",
        action=lambda ctx: ctx.update({"submitted": True}),
    )
    ctx = {}
    sm.send("submit", ctx)
    assert ctx.get("submitted") is True


def test_action_error_does_not_change_state():
    sm = StateMachine(initial="draft")

    def bad_action(ctx):
        raise RuntimeError("warehouse offline")

    sm.transition("submit", from_state="draft", to_state="submitted", action=bad_action)
    result = sm.send("submit", {})
    assert result.accepted is False
    assert sm.current_state == "draft"
    assert "warehouse offline" in result.reason


def test_history_tracks_accepted_transitions():
    sm = StateMachine(initial="draft")
    sm.transition("submit", from_state="draft", to_state="submitted")
    sm.transition("process", from_state="submitted", to_state="processing")
    sm.send("submit", {})
    sm.send("process", {})
    assert len(sm.history) == 2
    assert sm.history[0].from_state == "draft"
    assert sm.history[0].to_state == "submitted"
    assert sm.history[1].from_state == "submitted"
    assert sm.history[1].to_state == "processing"


def test_rejected_transition_not_in_history():
    sm = StateMachine(initial="draft")
    sm.transition("submit", from_state="draft", to_state="submitted", guard="score > 50")
    sm.send("submit", {"score": 10})
    assert len(sm.history) == 0


def test_can_returns_true():
    sm = StateMachine(initial="draft")
    sm.transition("submit", from_state="draft", to_state="submitted")
    assert sm.can("submit") is True


def test_can_returns_false_wrong_state():
    sm = StateMachine(initial="processing")
    sm.transition("submit", from_state="draft", to_state="submitted")
    assert sm.can("submit") is False


def test_can_respects_guard():
    sm = StateMachine(initial="draft")
    sm.transition("submit", from_state="draft", to_state="submitted", guard="score > 50")
    assert sm.can("submit", {"score": 80}) is True
    assert sm.can("submit", {"score": 10}) is False


def test_reset_to_initial():
    sm = StateMachine(initial="draft")
    sm.transition("submit", from_state="draft", to_state="submitted")
    sm.send("submit", {})
    sm.reset()
    assert sm.current_state == "draft"
    assert sm.history == []


def test_reset_to_specific_state():
    sm = StateMachine(initial="draft")
    sm.reset("processing")
    assert sm.current_state == "processing"


def test_duplicate_transition_raises():
    sm = StateMachine(initial="draft")
    sm.transition("submit", from_state="draft", to_state="submitted")
    with pytest.raises(ValueError):
        sm.transition("submit", from_state="draft", to_state="cancelled")


def test_duplicate_partial_overlap_raises():
    sm = StateMachine(initial="draft")
    sm.transition("cancel", from_state=["draft", "submitted"], to_state="cancelled")
    with pytest.raises(ValueError):
        sm.transition("cancel", from_state=["submitted", "processing"], to_state="cancelled")


def test_invalid_guard_raises_at_registration():
    sm = StateMachine(initial="draft")
    with pytest.raises(ValueError):
        sm.transition("submit", from_state="draft", to_state="submitted",
                      guard="this >>> is invalid")


def test_states_property():
    sm = StateMachine(initial="draft")
    sm.transition("submit", from_state="draft", to_state="submitted")
    sm.transition("cancel", from_state=["draft", "submitted"], to_state="cancelled")
    assert sm.states == {"draft", "submitted", "cancelled"}


def test_fluent_chaining():
    sm = (
        StateMachine(initial="a")
        .transition("go", from_state="a", to_state="b")
        .transition("go", from_state="b", to_state="c")
    )
    sm.send("go", {})
    sm.send("go", {})
    assert sm.current_state == "c"


def test_same_event_different_source_states():
    sm = StateMachine(initial="draft")
    sm.transition("go", from_state="draft", to_state="submitted")
    sm.transition("go", from_state="submitted", to_state="processing")
    sm.send("go", {})
    assert sm.current_state == "submitted"
    sm.send("go", {})
    assert sm.current_state == "processing"


def test_guard_missing_field_rejected():
    sm = StateMachine(initial="draft")
    sm.transition("submit", from_state="draft", to_state="submitted", guard="ghost > 10")
    result = sm.send("submit", {})
    assert result.accepted is False
    assert "Guard error" in result.reason
    assert sm.current_state == "draft"
