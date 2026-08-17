# LRSI

[![CI](https://github.com/ANAMIZED/LRSI/actions/workflows/ci.yml/badge.svg)](https://github.com/ANAMIZED/LRSI/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-server-purple.svg)](src/lrsi/mcp/)

**LRSI (Local Recursive Self-Improvement) — Autonomous Agentic Operating System**

Sovereign, closed-loop system on dual Blackwell hardware (RTX 5090 + RTX 6000-series). Built on the real open **LRSI Runtime Core** ([marcuszimmermann365/IRSI](https://github.com/marcuszimmermann365/IRSI), v13.3.0) — a phase-based, event-sourced, fail-closed research runtime for controlled self-modification, interruptibility, auditability, and replayable decisions.

It is the hardened governance kernel every serious local RSI system needs. Every mutation of code, skills, prompts, harness, evaluators, or (bounded) model weights is forced through the same fail-closed boundary and append-only event trail.

**[Support Agentic OS Kernels ($99)](https://buy.stripe.com/bJecN63wObPv6Bf7Zm43S02)** · **[Agentic OS Cycle ($0.75)](https://buy.stripe.com/3cI14o8R8dXD3p3frO43S04)** · **[Public Goods Support](https://donate.stripe.com/00w5kE3wOg5L8Jn2F243S00)**

### Non-custodial USDC (preferred for agents)

| Network | Address | Explorer |
|---------|---------|----------|
| **Base** | `0xD3d0E9eDAe3Ac7bb199a8EAA761BdA423b878438` | [basescan](https://basescan.org/address/0xD3d0E9eDAe3Ac7bb199a8EAA761BdA423b878438) |
| **Ethereum** | `0xD3d0E9eDAe3Ac7bb199a8EAA761BdA423b878438` | [etherscan](https://etherscan.io/address/0xD3d0E9eDAe3Ac7bb199a8EAA761BdA423b878438) |
| **Solana** | `ETQwWf19axArsY493UfC6bxe2BmEzmzvCb58PPnC38A` | [solscan](https://solscan.io/account/ETQwWf19axArsY493UfC6bxe2BmEzmzvCb58PPnC38A) |

*Related:* [rui](https://github.com/ANAMIZED/rui) · [server-os](https://github.com/ANAMIZED/server-os) · [openmesha](https://github.com/ANAMIZED/openmesha) · [OpenGOS](https://github.com/ANAMIZED/OpenGOS) · [agenticarb](https://github.com/ANAMIZED/agenticarb) · [x402-cloudflare-starter](https://github.com/ANAMIZED/x402-cloudflare-starter)

A senior engineer who has never seen this repository can, using **only** the source code and this `README.md`:

1. Stand up the LRSI Runtime Core and verify the self-modification boundary
2. Wire local model serving (vLLM / SGLang) on dual GPUs
3. Run a concrete improvement loop under the LRSI gates
4. Expand under the same invariants

---

## Quick Start (Hero Path)

```bash
# Outer stack (this repo) — offline, deterministic
pip install -e ".[dev]"
bash scripts/verify.sh
# 16 checks. All must pass.

# Optional: foundation Runtime Core
git clone https://github.com/marcuszimmermann365/IRSI.git
cd IRSI
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"          # or ".[live]" for real LLM support
python runner.py --iterations 3 --storage-path run_log.json --memory-path memory_store.json
python -m pytest -q -rs
python scripts/check_phase_event_coverage.py --run-sample --iterations 3
```

Default mode for the outer stack is **offline / mock** where possible. Point live endpoints at local vLLM/SGLang.

For full architecture, roadmap, hardware fit, and surfaces, see the repository documentation and `scripts/verify.sh`.

## Surfaces

| Surface | Entry |
|---------|-------|
| **LRSI Runtime Core** | External: [marcuszimmermann365/IRSI](https://github.com/marcuszimmermann365/IRSI) |
| CLI | `lrsi status` / `lrsi agents …` / `lrsi workflow` / `lrsi mutate` / `lrsi audit` |
| SDK | `from lrsi.sdk import LRSIClient` |
| MCP Server | `lrsi-mcp` / `src/lrsi/mcp/` |
| Multi-agent workflows | improver → evaluator → council under GateEngine |
| Skills | `skills/*/SKILL.md` (5 packages) |
| Audit | hash-chained trail + `verify_chain()` |
| AGENTS.md | Coding-agent contract at repo root |
| Verify | `bash scripts/verify.sh` |

## Verify contract

```bash
pip install -e ".[dev]"
bash scripts/verify.sh
```

Covers structure, skills, gate/audit, multi-agent workflows, SDK, CLI, MCP, and tests. **16 checks. All must pass.**

## Design principles

1. Fail closed
2. Every mutation through the LRSI boundary
3. Event-sourced audit trail
4. Evidence-gated promotion (no self-report)
5. Reversible harness plugins (temporal + spatial composability)
6. Local-first, sovereign, interruptible

## License

Apache-2.0
