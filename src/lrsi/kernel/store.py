"""In-memory process table + append-only event store for LRSI outer stack."""

from __future__ import annotations

from typing import Any

from lrsi.kernel.models import (
    AgentProcess,
    AuditEvent,
    GateRecord,
    MutationProposal,
    Task,
    Workflow,
    hash_event,
)


class ProcessTable:
    """Fail-closed in-memory store with hash-chained audit trail."""

    def __init__(self) -> None:
        self.agents: dict[str, AgentProcess] = {}
        self.tasks: dict[str, Task] = {}
        self.mutations: dict[str, MutationProposal] = {}
        self.gates: dict[str, GateRecord] = {}
        self.workflows: dict[str, Workflow] = {}
        self.audit: list[AuditEvent] = []
        self._last_hash: str = "genesis"

    # --- agents ---
    def create_agent(self, agent: AgentProcess) -> AgentProcess:
        self.agents[agent.id] = agent
        self._emit("agent.created", "GO", f"Agent {agent.name} created", agent_id=agent.id)
        return agent

    def get_agent(self, agent_id: str) -> AgentProcess | None:
        return self.agents.get(agent_id)

    def list_agents(self) -> list[AgentProcess]:
        return list(self.agents.values())

    # --- tasks ---
    def create_task(self, task: Task) -> Task:
        self.tasks[task.id] = task
        return task

    def update_task(self, task: Task) -> None:
        self.tasks[task.id] = task

    # --- mutations ---
    def create_mutation(self, mut: MutationProposal) -> MutationProposal:
        self.mutations[mut.id] = mut
        self._emit(
            "mutation.proposed",
            "GO",
            f"Mutation proposed: {mut.kind.value} on {mut.target}",
            mutation_id=mut.id,
            agent_id=mut.proposer_id,
            data={"kind": mut.kind.value, "target": mut.target},
        )
        return mut

    def get_mutation(self, mut_id: str) -> MutationProposal | None:
        return self.mutations.get(mut_id)

    # --- gates ---
    def record_gate(self, gate: GateRecord) -> GateRecord:
        self.gates[gate.id] = gate
        decision = gate.final_decision.value
        self._emit(
            "gate.final",
            decision,
            f"Final gate {decision} for {gate.mutation_id}",
            mutation_id=gate.mutation_id,
            data={"mutation_blocked": gate.mutation_blocked, "phases": len(gate.phases)},
        )
        return gate

    # --- workflows ---
    def create_workflow(self, wf: Workflow) -> Workflow:
        self.workflows[wf.id] = wf
        return wf

    def update_workflow(self, wf: Workflow) -> None:
        self.workflows[wf.id] = wf

    # --- audit ---
    def _emit(
        self,
        kind: str,
        decision: str,
        reason: str,
        agent_id: str | None = None,
        mutation_id: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> AuditEvent:
        payload = f"{kind}|{decision}|{reason}|{agent_id}|{mutation_id}"
        event_hash = hash_event(self._last_hash, payload)
        ev = AuditEvent(
            kind=kind,
            decision=decision,
            reason=reason,
            agent_id=agent_id,
            mutation_id=mutation_id,
            data=data or {},
            prev_hash=self._last_hash,
            event_hash=event_hash,
        )
        self.audit.append(ev)
        self._last_hash = event_hash
        return ev

    def audit_log(self) -> list[dict[str, Any]]:
        return [e.model_dump(mode="json") for e in self.audit]

    def verify_chain(self) -> bool:
        """Verify hash-chain integrity of the audit trail."""
        prev = "genesis"
        for ev in self.audit:
            payload = f"{ev.kind}|{ev.decision}|{ev.reason}|{ev.agent_id}|{ev.mutation_id}"
            expected = hash_event(prev, payload)
            if expected != ev.event_hash or ev.prev_hash != prev:
                return False
            prev = ev.event_hash
        return True

    def metrics(self) -> dict[str, float]:
        return {
            "agents_created": float(len(self.agents)),
            "mutations_proposed": float(len(self.mutations)),
            "gates_recorded": float(len(self.gates)),
            "workflows": float(len(self.workflows)),
            "audit_events": float(len(self.audit)),
            "chain_ok": 1.0 if self.verify_chain() else 0.0,
        }
