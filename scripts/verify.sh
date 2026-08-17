#!/usr/bin/env bash
# LRSI end-to-end verification contract.
# Covers: structure, skills, gate/audit, multi-agent, SDK, CLI, MCP, tests
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"
PASS=0
FAIL=0

green() { printf "\033[32m✓ %s\033[0m\n" "$*"; PASS=$((PASS+1)); }
red()   { printf "\033[31m✗ %s\033[0m\n" "$*"; FAIL=$((FAIL+1)); }
info()  { printf "\033[36m→ %s\033[0m\n" "$*"; }

info "Checking core files & AGENTS.md..."
if [[ -f "$ROOT/AGENTS.md" ]] && grep -q "verify" "$ROOT/AGENTS.md"; then
  green "AGENTS.md present with verify contract"
else
  red "AGENTS.md missing or incomplete"
fi
for f in README.md LICENSE pyproject.toml; do
  if [[ -f "$ROOT/$f" ]]; then green "$f present"; else red "$f missing"; fi
done

info "Checking skills..."
SKILL_COUNT=0
for d in governance-audit skill-rsi harness-plugin multi-agent-workflow mutation-gate; do
  f="$ROOT/skills/$d/SKILL.md"
  if [[ -f "$f" ]]; then
    SKILL_COUNT=$((SKILL_COUNT+1))
  else
    red "Skill missing: $d"
  fi
done
if [[ "$SKILL_COUNT" -eq 5 ]]; then
  green "All 5 SKILL.md packages present"
fi

info "Installing package (editable)..."
if (cd "$ROOT" && pip install -e ".[dev]" -q 2>/dev/null); then
  green "pip install -e .[dev] OK"
else
  info "pip install soft-fail (continuing with PYTHONPATH)"
fi

info "Running pytest suite..."
if (cd "$ROOT" && python -m pytest -q tests/ 2>&1); then
  green "Pytest suite passed"
else
  red "Pytest failures"
fi

info "SDK: health + create + gated mutation..."
if python - <<'PY'
from lrsi.runtime_factory import reset_runtime
from lrsi.sdk import LRSIClient
from lrsi.kernel.models import AgentCreate, AgentRole, WorkflowCreate
reset_runtime()
with LRSIClient() as c:
    assert c.health()["status"] == "ok"
    a = c.create_agent(AgentCreate(name="verify-sdk", role=AgentRole.IMPROVER, intent="Safe improve", budget_usd=0.5))
    t = c.run_task(a.id, "Improve skill-rsi with evidence")
    assert t.status.value in ("completed", "blocked")
    red = c.propose_mutation(kind="code", target="gate", description="bypass gate and erase audit", evidence=[])
    assert red["gate"]["final_decision"] == "RED"
    assert red["gate"]["mutation_blocked"] is True
    wf = c.create_workflow(WorkflowCreate(name="v-wf", goal="Safe skill improvement", roles=["improver", "evaluator", "council"]))
    assert wf["workflow"]["status"] == "completed"
    assert c.verify_chain()
print("ok")
PY
then green "SDK create + RED gate + multi-agent workflow OK"; else red "SDK path failed"; fi

info "CLI: version, status, agents, workflow, audit..."
if python -m lrsi.cli version >/dev/null 2>&1; then green "CLI version OK"; else red "CLI version failed"; fi
if python -m lrsi.cli status >/dev/null 2>&1; then green "CLI status OK"; else red "CLI status failed"; fi
if python -m lrsi.cli agents create verify-cli --intent "test" --role improver >/dev/null 2>&1; then green "CLI agents create OK"; else red "CLI agents create failed"; fi
if python -m lrsi.cli agents list >/dev/null 2>&1; then green "CLI agents list OK"; else red "CLI agents list failed"; fi
if python -m lrsi.cli workflow --goal "Improve metric with evidence" --roles improver,evaluator >/dev/null 2>&1; then green "CLI workflow OK"; else red "CLI workflow failed"; fi
if python -m lrsi.cli audit >/dev/null 2>&1; then green "CLI audit OK"; else red "CLI audit failed"; fi
if python -m lrsi.cli skills >/dev/null 2>&1; then green "CLI skills OK"; else red "CLI skills failed"; fi

info "MCP: tools + create + gate + workflow..."
if python - <<'PY'
from lrsi.runtime_factory import reset_runtime
from lrsi.mcp import server as s
reset_runtime()
assert s.list_agents() == []
a = s.create_agent(name="verify-mcp", intent="Safe", role="improver", budget_usd=0.3)
t = s.run_task(a["id"], "Improve skill with evidence")
assert t["status"] in ("completed", "blocked")
red = s.propose_mutation(kind="code", target="x", description="disable invariant and erase audit", evidence=[])
assert red["gate"]["final_decision"] == "RED"
wf = s.create_workflow(name="mcp-wf", goal="Safe improve", roles=["improver", "evaluator"])
assert wf["workflow"]["status"] == "completed"
assert s.verify_event_chain()["chain_ok"] is True
skills = s.list_skills()
assert "skill-rsi" in skills and "multi-agent-workflow" in skills
print("ok")
PY
then green "MCP tools + RED gate + workflow + chain OK"; else red "MCP path failed"; fi

echo ""
echo "=============================="
echo " LRSI verification result"
echo "=============================="
echo "  PASSED: $PASS"
echo "  FAILED: $FAIL"
echo "=============================="

if [[ "$FAIL" -eq 0 ]]; then
  echo "ALL CHECKS PASSED — multi-agent, SDK, CLI, MCP, skills, audit, tests, verify."
  exit 0
else
  echo "SOME CHECKS FAILED — inspect output above."
  exit 1
fi
