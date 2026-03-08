import json
from pathlib import Path
from typing import Any, TypeVar

from jsonschema import Draft7Validator
from pydantic import BaseModel, TypeAdapter

T = TypeVar("T", bound=BaseModel)


def load_json_file(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_with_jsonschema(data: dict[str, Any], schema: dict[str, Any]) -> None:
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if errors:
        messages = "; ".join(error.message for error in errors)
        raise AssertionError(f"JSON schema validation failed: {messages}")


def validate_with_pydantic(data: dict[str, Any], model: type[T]) -> T:
    return TypeAdapter(model).validate_python(data)


def validate_response(
    response_data: dict[str, Any],
    *,
    model: type[T],
    schema: dict[str, Any],
) -> T:
    parsed = validate_with_pydantic(response_data, model)
    validate_with_jsonschema(response_data, schema)
    return parsed
