import pytest
from state_machine.evaluator import evaluate, EvaluationError, parse_condition


def test_simple_comparison_true():
    assert evaluate("score > 50", {"score": 80}) is True


def test_simple_comparison_false():
    assert evaluate("score > 50", {"score": 20}) is False


def test_equality():
    assert evaluate('status == "active"', {"status": "active"}) is True
    assert evaluate('status == "active"', {"status": "inactive"}) is False


def test_and_operator():
    ctx = {"a": 1, "b": 2}
    assert evaluate("a > 0 AND b > 0", ctx) is True
    assert evaluate("a > 0 AND b > 5", ctx) is False


def test_or_operator():
    ctx = {"a": 1, "b": 2}
    assert evaluate("a > 5 OR b > 1", ctx) is True
    assert evaluate("a > 5 OR b > 5", ctx) is False


def test_not_operator():
    assert evaluate('NOT status == "active"', {"status": "inactive"}) is True
    assert evaluate('NOT status == "active"', {"status": "active"}) is False


def test_nested_field():
    ctx = {"order": {"total": 150}}
    assert evaluate("order.total > 100", ctx) is True
    assert evaluate("order.total > 200", ctx) is False


def test_deeply_nested_field():
    ctx = {"user": {"address": {"city": "KL"}}}
    assert evaluate('user.address.city == "KL"', ctx) is True


def test_in_operator():
    ctx = {"tier": "gold"}
    assert evaluate('tier IN ["gold", "platinum"]', ctx) is True
    assert evaluate('tier IN ["silver", "bronze"]', ctx) is False


def test_not_in_operator():
    ctx = {"country": "US"}
    assert evaluate('country NOT IN ["MY", "SG"]', ctx) is True
    assert evaluate('country NOT IN ["US", "UK"]', ctx) is False


def test_null_comparison():
    assert evaluate("status == null", {"status": None}) is True
    assert evaluate("status == null", {"status": "active"}) is False


def test_boolean_literal():
    assert evaluate("verified == true", {"verified": True}) is True
    assert evaluate("verified == false", {"verified": True}) is False


def test_missing_field_raises():
    with pytest.raises(EvaluationError):
        evaluate("ghost > 10", {})


def test_missing_nested_field_raises():
    with pytest.raises(EvaluationError):
        evaluate("order.total > 10", {})


def test_invalid_syntax_raises():
    with pytest.raises(ValueError):
        parse_condition("x >>> 10")


def test_short_circuit_or_skips_missing_field():
    assert evaluate("x > 0 OR missing.field == 1", {"x": 5}) is True


def test_short_circuit_and_skips_missing_field():
    assert evaluate("x > 100 AND missing.field == 1", {"x": 5}) is False


def test_operator_precedence():
    # AND binds tighter: A OR B AND C = A OR (B AND C)
    ctx = {"a": True, "b": False, "c": True}
    assert evaluate("a == true OR b == true AND c == true", ctx) is True


def test_empty_list_in():
    assert evaluate("x IN []", {"x": 1}) is False


def test_empty_list_not_in():
    assert evaluate("x NOT IN []", {"x": 1}) is True
