---
name: multi-agent-workflow
description: Orchestrate improver → evaluator → council under LRSI gates
---

# Skill: multi-agent-workflow

## Purpose
Run a sequential multi-agent workflow where every proposed mutation is forced through the LRSI Runtime Core boundary (PreProposalAdversarial → Final Gate).

## Roles
- **improver**: observes outcomes and proposes bounded mutations
- **evaluator**: scores on held-out metrics (never self-report)
- **council**: votes GO / HOLD given independent evidence

## Rules
1. All mutations submit exclusively through the gate engine.
2. RED in PreProposalAdversarial is terminal.
3. Promotion only on clear held-out improvement + Final Gate GO.
4. Full event trail recorded.
