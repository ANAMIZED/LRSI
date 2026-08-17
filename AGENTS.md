# AGENTS.md — LRSI

This file is the contract for any AI coding agent working on this repository.

## What this project is

LRSI is an Autonomous Agentic Operating System for Local Recursive Self-Improvement. It is built around the LRSI Runtime Core (marcuszimmermann365/IRSI v13.3.0) as the fail-closed governance kernel. The outer layers (hot-swappable harness, outer improver, executable gym, bounded model evolution) force every mutation through the same event-sourced, invariant-protected boundary.

A senior engineer with only the source code and README.md must be able to stand up the foundation, wire local inference, run a gated improvement loop, and expand under the invariants.

## How to run & verify

```bash
# Foundation (external core)
git clone https://github.com/marcuszimmermann365/IRSI.git && cd IRSI
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python runner.py --iterations 3 --storage-path run_log.json --memory-path memory_store.json
python -m pytest -q -rs

# This repo (outer stack)
pip install -e ".[dev]"
bash scripts/verify.sh
pytest -q
```

## Hard rules for agents

1. Never break the verify contract.
2. Fail closed. Every mutation of code, skills, prompts, harness, or weights must go through the LRSI gate boundary.
3. RED decisions in PreProposalAdversarial are terminal. Do not soften them.
4. Evidence-gated promotion only — independent held-out metrics, never self-report.
5. Keep plugins reversible (temporal + spatial composability).
6. Prefer small, focused changes. Update README.md and AGENTS.md when public surfaces change.
7. Do not introduce ambient authority or bypass the event-sourced audit trail.

## Surfaces that must stay working

| Surface | Entry |
|---------|-------|
| CLI | `lrsi status` / `lrsi agents …` / `lrsi workflow` / `lrsi mutate` / `lrsi audit` |
| SDK | `from lrsi.sdk import LRSIClient` |
| MCP | `lrsi-mcp` / `from lrsi.mcp.server import mcp` |
| Multi-agent workflows | improver → evaluator → council under GateEngine |
| Skills | `skills/*/SKILL.md` (5 packages) |
| Audit | hash-chained append-only trail + `verify_chain()` |
| Tests | `pytest -q` |
| Verify | `bash scripts/verify.sh` |
