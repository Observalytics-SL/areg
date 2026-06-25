#!/usr/bin/env python3
"""Validate AREG examples against the registry-entry JSON Schema."""

import json
import sys
from pathlib import Path

try:
    import jsonschema
    from jsonschema import Draft202012Validator
except ImportError:
    sys.exit("Install jsonschema first:  pip install jsonschema")

REPO_ROOT = Path(__file__).parent.parent
SCHEMA_DIR = REPO_ROOT / "schema"
EXAMPLES_DIR = REPO_ROOT / "examples"

STRIP_KEYS = {"_comment"}


def load_schema():
    path = SCHEMA_DIR / "registry-entry.schema.json"
    if not path.exists():
        sys.exit(f"Schema not found: {path}")
    with path.open() as f:
        return json.load(f), path


def validate_example(path: Path, schema_def: dict, schema_path: Path):
    with path.open() as f:
        raw = json.load(f)
    instance = {k: v for k, v in raw.items() if k not in STRIP_KEYS}
    try:
        Draft202012Validator(schema_def).validate(instance)
        print(f"  PASS  {path.name}  ({schema_path.name})")
        return True
    except jsonschema.ValidationError as e:
        print(f"  FAIL  {path.name}: {e.message}")
        return False


def main():
    schema_def, schema_path = load_schema()
    examples = sorted(EXAMPLES_DIR.glob("*.json"))
    if not examples:
        sys.exit(f"No examples found in {EXAMPLES_DIR}")

    passed = failed = 0
    for ex in examples:
        if validate_example(ex, schema_def, schema_path):
            passed += 1
        else:
            failed += 1

    print(f"\n{passed} valid, {failed} failed")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
