#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_test_file(openapi_path: Path, output_path: Path) -> None:
    spec = json.loads(openapi_path.read_text(encoding="utf-8"))
    paths = spec.get("paths", {})

    lines = [
        "import pytest",
        "",
        "",
    ]

    for path, methods in paths.items():
        for method in methods:
            method_upper = method.upper()
            test_name = f"test_{method}_{path.strip('/').replace('/', '_').replace('{', '').replace('}', '')}"
            lines.extend(
                [
                    "@pytest.mark.api",
                    f"def {test_name}():",
                    f"    # TODO: implement test for {method_upper} {path}",
                    "    assert True",
                    "",
                ]
            )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate pytest test stubs from OpenAPI")
    parser.add_argument("--openapi", default="openapi/openapi.json", help="Path to OpenAPI JSON")
    parser.add_argument("--out", default="tests/api/test_generated_openapi.py", help="Output test file")
    args = parser.parse_args()

    openapi_path = Path(args.openapi)
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    build_test_file(openapi_path, output_path)
    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
