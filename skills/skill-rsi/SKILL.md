---
name: skill-rsi
description: Skill-RSI style improvement loop under LRSI gates
---

# Skill: skill-rsi

## Purpose
Run a Skill-RSI style improvement loop for a single skill family under LRSI gates.

## Loop
1. Research / ontology grounding
2. Propose bounded challenger skill (one variable)
3. Submit candidate exclusively through LRSI Mutation → PreProposalAdversarial → ... → Final Gate
4. Evaluate on held-out metrics in the executable gym
5. Evidence-based promotion only (champion vs challenger)

## Rules
- Never promote on self-report.
- Keep one-variable-at-a-time discipline early.
- Record full event trail.
