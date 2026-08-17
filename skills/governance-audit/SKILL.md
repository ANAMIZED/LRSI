# Skill: governance-audit

## Purpose
Verify that every mutation path is forced through the LRSI Runtime Core self-modification boundary and that event-chain integrity holds.

## Inputs
- Path to events JSONL or run_log
- Optional: candidate mutation description

## Outputs
- Pass / Fail with concrete invariant violations (if any)
- Hash-chain verification summary

## Rules
- RED in PreProposalAdversarial is terminal — never softens.
- No HOLD-state mutations allowed.
- All PhaseResults must emit phase.result events.
