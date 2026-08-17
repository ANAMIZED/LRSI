---
name: mutation-gate
description: Propose and evaluate mutations under the fail-closed LRSI gate
---

# Skill: mutation-gate

## Purpose
Propose a single bounded mutation (skill / prompt / code / harness / weights) and force it through the full LRSI phase pipeline.

## Critical invariants
- PreProposalAdversarial RED is terminal (`mutation_blocked=true`)
- Never soften Council RED into GO
- No HOLD-state mutations
- Evidence required for weight updates
- Append-only hash-chained audit

## Usage
```bash
lrsi mutate --kind skill --target skill-rsi --desc "Improve metric" --evidence held_out_v1
```
