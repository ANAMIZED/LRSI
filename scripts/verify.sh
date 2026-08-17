#!/usr/bin/env bash
set -euo pipefail

echo "=== LRSI verify contract ==="

# Structure checks
test -f README.md
test -f AGENTS.md
test -f LICENSE
test -f pyproject.toml
test -d src/lrsi
test -d skills
test -d tests
test -d scripts

echo "[ok] core files present"

# Skills present
for skill in governance-audit skill-rsi harness-plugin; do
  test -f "skills/${skill}/SKILL.md" || { echo "missing skill: ${skill}"; exit 1; }
done
echo "[ok] skills present"

# Python package importable (if installed)
if python -c "import lrsi" 2>/dev/null; then
  echo "[ok] lrsi package importable"
else
  echo "[info] lrsi not installed in current env (run: pip install -e . )"
fi

echo "=== All structural checks passed ==="
echo "Next: stand up IRSI Runtime Core and wire Phase 1."
