#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def to_class_name(name: str) -> str:
    return "".join(part.capitalize() for part in name.replace("-", "_").split("_"))


def map_field_type(property_schema: dict[str, str]) -> str:
    type_mapping = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "array": "list",
        "object": "dict",
    }
    return type_mapping.get(property_schema.get("type", "string"), "str")


def generate_models(openapi_path: Path, output_path: Path) -> None:
    spec = json.loads(openapi_path.read_text(encoding="utf-8"))
    schemas = spec.get("components", {}).get("schemas", {})

    lines = ["from pydantic import BaseModel", "", ""]

    for schema_name, schema_def in schemas.items():
        class_name = to_class_name(schema_name)
        lines.append(f"class {class_name}(BaseModel):")
        properties = schema_def.get("properties", {})

        if not properties:
            lines.append("    pass")
        else:
            for prop_name, prop_schema in properties.items():
                py_type = map_field_type(prop_schema)
                lines.append(f"    {prop_name}: {py_type}")

        lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate pydantic model stubs from OpenAPI")
    parser.add_argument("--openapi", default="openapi/openapi.json", help="Path to OpenAPI JSON")
    parser.add_argument("--out", default="models/generated_models.py", help="Output Python models file")
    args = parser.parse_args()

    generate_models(Path(args.openapi), Path(args.out))
    print(f"Generated {args.out}")


if __name__ == "__main__":
    main()
