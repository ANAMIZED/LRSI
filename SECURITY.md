# Security Policy

## Reporting a Vulnerability

Please report security issues privately by opening a draft security advisory on this repository or contacting the maintainers directly.

## Design Stance

LRSI is fail-closed by construction. Every self-modification is forced through the LRSI Runtime Core boundary with:

- Terminal RED decisions in PreProposalAdversarial
- 11 central invariants
- Append-only, hash-chained event sourcing
- Optional signed events + WORM sinks in production mode

Do not weaken these controls. Evidence-gated promotion and reversible plugins are mandatory.
