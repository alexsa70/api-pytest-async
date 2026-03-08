from __future__ import annotations

from typing import Any


def diff_schemas(left: dict[str, Any], right: dict[str, Any], path: str = "$") -> list[str]:
    differences: list[str] = []

    left_keys = set(left.keys())
    right_keys = set(right.keys())

    for key in sorted(left_keys - right_keys):
        differences.append(f"{path}.{key}: missing in right schema")

    for key in sorted(right_keys - left_keys):
        differences.append(f"{path}.{key}: missing in left schema")

    for key in sorted(left_keys & right_keys):
        left_value = left[key]
        right_value = right[key]
        current_path = f"{path}.{key}"

        if type(left_value) is not type(right_value):
            differences.append(
                f"{current_path}: type mismatch ({type(left_value).__name__} != {type(right_value).__name__})"
            )
            continue

        if isinstance(left_value, dict):
            differences.extend(diff_schemas(left_value, right_value, current_path))
        elif isinstance(left_value, list):
            if len(left_value) != len(right_value):
                differences.append(
                    f"{current_path}: list length mismatch ({len(left_value)} != {len(right_value)})"
                )
        elif left_value != right_value:
            differences.append(f"{current_path}: value mismatch ({left_value!r} != {right_value!r})")

    return differences
