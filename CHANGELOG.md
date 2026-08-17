# Changelog

## [0.1.0] — 2026-08-17

### Added
- Full outer-stack scaffolding mirroring Server OS layout.
- **Multi-agent workflows**: improver → evaluator → council under GateEngine.
- **SDK**: `LRSIClient` (create agents, run tasks, propose mutations, workflows, audit).
- **CLI**: `lrsi status|agents|mutate|workflow|audit|metrics|skills`.
- **MCP server**: tools for agents, mutations, workflows, audit, chain verification.
- **Fail-closed gate engine**: PreProposalAdversarial (terminal RED), DGM precheck, evaluation, council, Final Gate; hash-chained audit trail.
- **Skills**: governance-audit, skill-rsi, harness-plugin, multi-agent-workflow, mutation-gate.
- **Tests**: smoke, CLI, SDK, MCP (pytest).
- **Verify contract**: `bash scripts/verify.sh` exercises all surfaces offline.
- Architecture + build roadmap for dual-Blackwell local RSI.
