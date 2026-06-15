import operator
from typing import Any
from pyparsing import (
    Combine, Group, Keyword, Literal, Opt, ParseException, ParseResults,
    QuotedString, Suppress, Word, ZeroOrMore, alphanums, alphas,
    infix_notation, one_of, opAssoc, pyparsing_common, replace_with,
)


class EvaluationError(Exception):
    pass


_OPS = {
    ">":  operator.gt,
    "<":  operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}

_KEYWORDS = (
    Keyword("AND") | Keyword("OR") | Keyword("NOT") |
    Keyword("IN")  | Keyword("true") | Keyword("false") | Keyword("null")
)

_field = Combine(
    (~_KEYWORDS + Word(alphas + "_", alphanums + "_")) +
    ZeroOrMore(Literal(".") + Word(alphas + "_", alphanums + "_"))
)

_number = pyparsing_common.number()
_string = QuotedString('"') | QuotedString("'")
_true   = Keyword("true").set_parse_action(replace_with(True))
_false  = Keyword("false").set_parse_action(replace_with(False))
_null   = Keyword("null").set_parse_action(replace_with(None))
_value  = _number | _string | _true | _false | _null

_op = one_of(">= <= != == > <")
_comparison = Group(_field + _op + _value)

_value_list  = Group(Suppress("[") + Opt(_value + ZeroOrMore(Suppress(",") + _value)) + Suppress("]"))
_in_expr     = Group(_field + Keyword("IN")  + _value_list)
_not_in_expr = Group(_field + Keyword("NOT") + Keyword("IN") + _value_list)

_atom = _not_in_expr | _in_expr | _comparison

_EXPR = infix_notation(_atom, [
    (Keyword("NOT"), 1, opAssoc.RIGHT),
    (Keyword("AND"), 2, opAssoc.LEFT),
    (Keyword("OR"),  2, opAssoc.LEFT),
])


def parse_condition(condition: str):
    try:
        return _EXPR.parse_string(condition, parse_all=True)[0]
    except ParseException as e:
        raise ValueError(f"Invalid condition syntax: {e}")


def _resolve(field_str: str, context: dict) -> Any:
    parts = field_str.split(".")
    current = context
    path = ""
    for part in parts:
        path = f"{path}.{part}" if path else part
        if isinstance(current, dict):
            if part not in current:
                raise EvaluationError(f"Field '{path}' not found in context")
            current = current[part]
        elif hasattr(current, part):
            current = getattr(current, part)
        else:
            raise EvaluationError(f"Cannot access '{part}' on {type(current).__name__}")
    return current


def _eval(node, context: dict) -> bool:
    items = list(node)

    if len(items) == 1:
        item = items[0]
        return _eval(item, context) if isinstance(item, ParseResults) else item

    if isinstance(items[0], str):
        field_str = items[0]
        op_str    = str(items[1])
        if op_str in _OPS:
            try:
                return _OPS[op_str](_resolve(field_str, context), items[2])
            except TypeError as e:
                raise EvaluationError(f"Type error in comparison '{field_str} {op_str} {items[2]}': {e}")
        if op_str == "IN":
            return _resolve(field_str, context) in list(items[2])
        if op_str == "NOT":
            return _resolve(field_str, context) not in list(items[3])

    if str(items[0]) == "NOT":
        return not _eval(items[1], context)

    result = _eval(items[0], context)
    i = 1
    while i < len(items):
        bool_op = str(items[i])
        if bool_op == "AND":
            if not result:
                return False
            result = _eval(items[i + 1], context)
        elif bool_op == "OR":
            if result:
                return True
            result = _eval(items[i + 1], context)
        else:
            raise EvaluationError(f"Unknown operator: {bool_op}")
        i += 2
    return result


def evaluate(condition: str, context: dict) -> bool:
    return _eval(parse_condition(condition), context)


def evaluate_parsed(parsed, context: dict) -> bool:
    return _eval(parsed, context)
