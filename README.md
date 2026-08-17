# LRSI

[![CI](https://github.com/ANAMIZED/LRSI/actions/workflows/ci.yml/badge.svg)](https://github.com/ANAMIZED/LRSI/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-server-purple.svg)](src/lrsi/mcp/)
[![SDK](https://img.shields.io/badge/SDK-Python-green.svg)](src/lrsi/sdk/)
[![CLI](https://img.shields.io/badge/CLI-lrsi-orange.svg)](src/lrsi/cli.py)
[![API](https://img.shields.io/badge/API-FastAPI-009688.svg)](src/lrsi/api/)

**LRSI (Local Recursive Self-Improvement) — Autonomous Agentic Operating System**

Sovereign, closed-loop system on dual Blackwell hardware. Built on the open **LRSI Runtime Core** ([marcuszimmermann365/IRSI](https://github.com/marcuszimmermann365/IRSI)). Every mutation is forced through a fail-closed boundary and append-only event trail.

**[Support Agentic OS Kernels ($99)](https://buy.stripe.com/bJecN63wObPv6Bf7Zm43S02)** · **[Agentic OS Cycle ($0.75)](https://buy.stripe.com/3cI14o8R8dXD3p3frO43S04)** · **[Public Goods Support](https://donate.stripe.com/00w5kE3wOg5L8Jn2F243S00)**

### Non-custodial USDC (preferred for agents)

| Network | Address |
|---------|---------|
| **Base / Ethereum** | `0xD3d0E9eDAe3Ac7bb199a8EAA761BdA423b878438` |
| **Solana** | `ETQwWf19axArsY493UfC6bxe2BmEzmzvCb58PPnC38A` |

*Related:* [rui](https://github.com/ANAMIZED/rui) · [server-os](https://github.com/ANAMIZED/server-os) · [openmesha](https://github.com/ANAMIZED/openmesha) · [OpenGOS](https://github.com/ANAMIZED/OpenGOS)

## Surfaces

| Surface | Entry |
|---------|-------|
| **CLI** | `lrsi status` / `lrsi workflow` / `lrsi mutate` / `lrsi audit` |
| **SDK** | `from lrsi.sdk import LRSIClient` |
| **REST API** | `lrsi-api` → http://localhost:8080/docs |
| **MCP Server** | `lrsi-mcp` |
| **Multi-agent** | improver → evaluator → council + `skills/multi-agent-workflow/` |
| **CI** | `.github/workflows/ci.yml` |
| **Verify** | `bash scripts/verify.sh` |

## Quick Start

```bash
pip install -e ".[dev,mcp,api]"
bash scripts/verify.sh
lrsi-api
```

## Design principles

1. Fail closed
2. Every mutation through the LRSI boundary
3. Event-sourced audit trail
4. Evidence-gated promotion
5. Multi-surface (CLI · SDK · API · MCP · workflows)

## License

Apache-2.0
