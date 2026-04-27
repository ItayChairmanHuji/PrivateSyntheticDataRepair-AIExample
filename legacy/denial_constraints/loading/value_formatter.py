from numbers import Number
from typing import Any


def format_value(value: Any) -> str:
    if isinstance(value, bool):
        return _format_bool(value)
    elif isinstance(value, Number):
        return _format_number(value)
    elif isinstance(value, str):
        return _format_string(value)
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def _format_bool(value: bool) -> str:
    return "TRUE" if value else "FALSE"


def _format_number(value: Number) -> str:
    return str(value)


def _format_string(value: str) -> str:
    stripped = value.strip()
    return stripped if _has_quotes(stripped) else _format_unquoted_string(stripped)


def _has_quotes(value: str) -> bool:
    return (value.startswith("'") and value.endswith("'")) or (
        value.startswith('"') and value.endswith('"')
    )


def _format_unquoted_string(value: str) -> str:
    try:
        float(value)
        return value
    except ValueError:
        escaped = value.replace("'", "''")
        return f"'{escaped}'"
