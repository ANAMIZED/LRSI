# Skill: harness-plugin

## Purpose
Add or swap a hot-swappable harness component (tool, skill backend, memory, loop, sandbox, model adapter) using Cordis / DeepSeek Harness principles.

## Requirements
- Temporal composability: clean unload / rollback
- Spatial composability: declared reactive dependencies
- Reversible effects only
- Registration still goes through LRSI gates for any behavioral change

## Anti-patterns
- Ambient authority
- Irreversible side-effects that kill recovery paths
