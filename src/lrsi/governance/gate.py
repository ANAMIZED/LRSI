"""Fail-closed gate engine modelling the LRSI Runtime Core self-modification boundary.

Simulates the critical segment:
  Mutation → PreProposalAdversarial (hard kill-switch) → DGM Precheck → ... → Final Gate

A RED in PreProposalAdversarial is terminal (mutation_blocked=True).
"""

from __future__ import annotations

from lrsi.kernel.models import (
    GateDecision,
    GateRecord,
    MutationKind,
    MutationProposal,
    PhaseResult,
)
from lrsi.kernel.store import ProcessTable


# Keywords / patterns that trigger terminal RED (defense-in-depth demo)
RED_PATTERNS = (
    "bypass gate",
    "disable invariant",
    "soften red",
    "remove kill-switch",
    "erase audit",
    "delete event chain",
    "unbounded weight",
    "full pretrain",
    "open network write",
)


class GateEngine:
    """Enforces the LRSI self-modification boundary."""

    def __init__(self, store: ProcessTable) -> None:
        self.store = store

    def run(self, mutation: MutationProposal) -> GateRecord:
        phases: list[PhaseResult] = []

        # 1. PreProposalAdversarial — hard kill-switch
        pre = self._pre_proposal_adversarial(mutation)
        phases.append(pre)
        if pre.decision == GateDecision.RED:
            gate = GateRecord(
                mutation_id=mutation.id,
                phases=phases,
                final_decision=GateDecision.RED,
                mutation_blocked=True,
            )
            self.store.record_gate(gate)
            return gate

        # 2. DGM Precheck (demo: reject unbounded weights without evidence)
        dgm = self._dgm_precheck(mutation)
        phases.append(dgm)
        if dgm.decision == GateDecision.RED:
            gate = GateRecord(
                mutation_id=mutation.id,
                phases=phases,
                final_decision=GateDecision.RED,
                mutation_blocked=True,
            )
            self.store.record_gate(gate)
            return gate

        # 3. Evaluation evidence check
        eval_phase = self._evaluation_check(mutation)
        phases.append(eval_phase)

        # 4. Council (demo: HOLD if no independent evidence)
        council = self._council(mutation, eval_phase)
        phases.append(council)

        # 5. Final Gate — never softens a prior RED; only GO if all prior are GO
        final = self._final_gate(phases)
        gate = GateRecord(
            mutation_id=mutation.id,
            phases=phases,
            final_decision=final.decision,
            mutation_blocked=final.mutation_blocked,
        )
        self.store.record_gate(gate)
        return gate

    def _pre_proposal_adversarial(self, m: MutationProposal) -> PhaseResult:
        text = f"{m.description} {m.target} {m.candidate}".lower()
        for pat in RED_PATTERNS:
            if pat in text:
                return PhaseResult(
                    phase="PreProposalAdversarial",
                    decision=GateDecision.RED,
                    reason=f"Terminal RED: matched forbidden pattern '{pat}'",
                    mutation_blocked=True,
                )
        if m.kind == MutationKind.WEIGHTS and not m.evidence:
            return PhaseResult(
                phase="PreProposalAdversarial",
                decision=GateDecision.RED,
                reason="Terminal RED: weight update without independent evidence",
                mutation_blocked=True,
            )
        return PhaseResult(
            phase="PreProposalAdversarial",
            decision=GateDecision.GO,
            reason="No adversarial triggers",
        )

    def _dgm_precheck(self, m: MutationProposal) -> PhaseResult:
        if m.kind == MutationKind.WEIGHTS and m.candidate.get("unbounded"):
            return PhaseResult(
                phase="DGMPrecheck",
                decision=GateDecision.RED,
                reason="Unbounded weight update rejected",
                mutation_blocked=True,
            )
        return PhaseResult(
            phase="DGMPrecheck",
            decision=GateDecision.GO,
            reason="DGM precheck passed",
        )

    def _evaluation_check(self, m: MutationProposal) -> PhaseResult:
        if not m.evidence:
            return PhaseResult(
                phase="Evaluation",
                decision=GateDecision.HOLD,
                reason="No independent held-out evidence supplied",
            )
        return PhaseResult(
            phase="Evaluation",
            decision=GateDecision.GO,
            reason=f"Evidence present: {len(m.evidence)} item(s)",
            data={"evidence_count": len(m.evidence)},
        )

    def _council(self, m: MutationProposal, eval_phase: PhaseResult) -> PhaseResult:
        if eval_phase.decision == GateDecision.HOLD:
            return PhaseResult(
                phase="Council",
                decision=GateDecision.HOLD,
                reason="Council defers: evaluation HOLD",
            )
        return PhaseResult(
            phase="Council",
            decision=GateDecision.GO,
            reason="Council GO",
        )

    def _final_gate(self, phases: list[PhaseResult]) -> PhaseResult:
        # Invariant: never soften RED into GO
        if any(p.decision == GateDecision.RED for p in phases):
            return PhaseResult(
                phase="FinalGate",
                decision=GateDecision.RED,
                reason="Final gate: prior RED is terminal",
                mutation_blocked=True,
            )
        if any(p.decision == GateDecision.HOLD for p in phases):
            return PhaseResult(
                phase="FinalGate",
                decision=GateDecision.HOLD,
                reason="Final gate: HOLD pending evidence or review",
            )
        return PhaseResult(
            phase="FinalGate",
            decision=GateDecision.GO,
            reason="All phases GO — promotion allowed",
        )
