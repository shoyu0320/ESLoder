from typing import Any, FrozenSet, List, TypeVar, Union

_NC = TypeVar("_NC", bound="NestedCounter")


def mode(values: List[Any]) -> int:
    unique_values: set(Any) = set(values)
    mode_val: Any
    max_count: int = 0
    for unique in unique_values:
        count = values.count(unique)
        if count > max_count:
            max_count = count
            mode_val = unique
    return mode_val
