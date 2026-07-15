"""Comparison operators. Each takes (actual, expected) and returns bool.
They may raise ValueError for un-evaluable input — the evaluator converts
that to Status.ERROR rather than letting it crash the audit."""


def _num(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"not numeric: {value!r}") from None


def op_equals(actual, expected) -> bool:
    return str(actual).lower() == str(expected).lower()


def op_not_equals(actual, expected) -> bool:
    return not op_equals(actual, expected)


def op_in(actual, expected) -> bool:
    if isinstance(expected, str | bytes):
        candidates = [expected]
    else:
        try:
            candidates = list(expected)
        except TypeError:
            candidates = [expected]
    return str(actual).lower() in [str(e).lower() for e in candidates]


def op_max(actual, expected) -> bool:
    """Passes when actual <= expected (e.g. maxauthtries at most 4)."""
    return _num(actual) <= _num(expected)


def op_min(actual, expected) -> bool:
    return _num(actual) >= _num(expected)


OPERATORS = {
    "equals": op_equals,
    "not_equals": op_not_equals,
    "in": op_in,
    "max": op_max,
    "min": op_min,
}
