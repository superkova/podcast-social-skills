#!/bin/bash
# Generate test visuals from JSON shape specs
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$SCRIPT_DIR/scripts/generate_visual.py"
TESTS_DIR="$SCRIPT_DIR/tests"
OUT="$TESTS_DIR/output"

mkdir -p "$OUT"

for json_file in "$TESTS_DIR"/*.json; do
  name=$(basename "$json_file" .json)
  echo "=== Rendering: $name ==="
  python "$SCRIPT" --shapes "$json_file" --output "$OUT/$name.png"
  echo ""
done

echo "All visuals generated in: $OUT"
ls -la "$OUT"/*.png
