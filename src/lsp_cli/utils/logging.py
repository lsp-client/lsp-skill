from __future__ import annotations

from collections.abc import Callable

import loguru


def extra_filter(
    key: str, value: object = None, *, exclude: bool = False
) -> Callable[[loguru.Record], bool]:
    """Create a loguru filter based on extra context.

    If value is None, it checks for the existence of the key.
    If exclude is True, it returns True for records NOT matching the criteria.

    Args:
        key: The key in record["extra"] to check.
        value: The value to match. If None, only checks for key existence.
        exclude: If True, invert the match result.

    Returns:
        A filter function for loguru.
    """

    def filter_func(record: Record) -> bool:
        if value is None:
            match = key in record["extra"]
        else:
            match = record["extra"].get(key) == value

        return not match if exclude else match

    return filter_func
