#!/bin/bash
# Generate test carousels for all themes and a logo-derived variant
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$SCRIPT_DIR/scripts/generate_carousel.py"
TESTS_DIR="$SCRIPT_DIR/tests"
OUT="$TESTS_DIR/output"

mkdir -p "$OUT"

echo "=== Professional theme (marketing content) ==="
python "$SCRIPT" \
  --slides "$TESTS_DIR/slides_marketing.json" \
  --palette professional \
  --company "GrowthLab" \
  --url "https://growthlab.io" \
  --output "$OUT/professional_marketing.pdf"

echo ""
echo "=== Bold theme (startup content) ==="
python "$SCRIPT" \
  --slides "$TESTS_DIR/slides_startup.json" \
  --palette bold \
  --company "LaunchPad" \
  --url "https://www.launchpad.vc/resources/bootstrapping-guide?ref=linkedin" \
  --output "$OUT/bold_startup.pdf"

echo ""
echo "=== Modern theme (design content) ==="
python "$SCRIPT" \
  --slides "$TESTS_DIR/slides_design.json" \
  --palette modern \
  --company "PixelCraft" \
  --url "https://pixelcraft.design" \
  --output "$OUT/modern_design.pdf"

echo ""
echo "=== Warm theme (coaching content) ==="
python "$SCRIPT" \
  --slides "$TESTS_DIR/slides_coaching.json" \
  --palette warm \
  --company "MindShift" \
  --url "https://mindshift.co" \
  --output "$OUT/warm_coaching.pdf"

echo ""
echo "=== Logo-derived theme (startup content + Prism logo) ==="
python "$SCRIPT" \
  --slides "$TESTS_DIR/slides_startup.json" \
  --logo "$TESTS_DIR/logo.png" \
  --company "Prism" \
  --url "https://prism.io" \
  --output "$OUT/logo_derived_startup.pdf"

echo ""
echo "=== Custom colors + logo (marketing content) ==="
python "$SCRIPT" \
  --slides "$TESTS_DIR/slides_marketing.json" \
  --colors "#0D1117,#58A6FF,#F78166" \
  --logo "$TESTS_DIR/logo.png" \
  --company "Prism" \
  --url "https://prism.io/blog" \
  --output "$OUT/custom_colors_marketing.pdf"

echo ""
echo "All test carousels generated in: $OUT"
ls -la "$OUT"/*.pdf
