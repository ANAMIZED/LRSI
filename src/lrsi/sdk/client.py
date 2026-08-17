"""LRSI Python SDK — typed client over the in-process outer stack.

(In production this can target an HTTP control plane; for verification
and local use it talks directly to the shared runtime.)
"""

from __future__ import annotations

from typing import Any

from lrsi.kernel.models import (
    AgentCreate,
    AgentProcess,
    MutationKind,
    MutationProposal,
    Task,
    WorkflowCreate,
)
from lrsi.runtime_factory import get_runtime, get_store


class LRSIClient:
    """Synchronous client for LRSI outer stack."""

    def __init__(self) -> None:
        self._rt = get_runtime()
        self._store = get_store()

    def close(self) -> None:
        pass

    def __enter__(self) -> "LRSIClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "mode": "in-process", "chain_ok": self._store.verify_chain()}

    def metrics(self) -> dict[str, float]:
        return self._store.metrics()

    def create_agent(self, body: AgentCreate | dict[str, Any]) -> AgentProcess:
        if isinstance(body, dict):
            body = AgentCreate(**body)
        return self._rt.create_agent(body)

    def list_agents(self) -> list[AgentProcess]:
        return self._store.list_agents()

    def get_agent(self, agent_id: str) -> AgentProcess:
        agent = self._store.get_agent(agent_id)
        if agent is None:
            raise KeyError(f"agent not found: {agent_id}")
        return agent

    def run_task(self, agent_id: str, goal: str) -> Task:
        agent = self.get_agent(agent_id)
        return self._rt.run_task(agent, goal)

    def propose_mutation(
        self,
        kind: str,
        target: str,
        description: str,
        candidate: dict[str, Any] | None = None,
        evidence: list[str] | None = None,
        proposer_id: str | None = None,
    ) -> dict[str, Any]:
        mut = MutationProposal(
            kind=MutationKind(kind),
            target=target,
            description=description,
            candidate=candidate or {},
            evidence=evidence or [],
            proposer_id=proposer_id,
        )
        self._store.create_mutation(mut)
        gate = self._rt.gate.run(mut)
        return {
            "mutation": mut.model_dump(mode="json"),
            "gate": gate.model_dump(mode="json"),
        }

    def create_workflow(self, body: WorkflowCreate | dict[str, Any]) -> dict[str, Any]:
        if isinstance(body, dict):
            body = WorkflowCreate(**body)
        return self._rt.run_workflow(body)

    def audit_log(self) -> list[dict[str, Any]]:
        return self._store.audit_log()

    def verify_chain(self) -> bool:
        return self._store.verify_chain()
