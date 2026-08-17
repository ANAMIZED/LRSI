"""Multi-agent runtime for LRSI outer stack.

Roles: improver, evaluator, council, researcher, harness.
All mutations are forced through GateEngine.
"""

from __future__ import annotations

from typing import Any

from lrsi.governance.gate import GateEngine
from lrsi.kernel.models import (
    AgentCreate,
    AgentProcess,
    AgentRole,
    AgentStatus,
    GateDecision,
    MutationKind,
    MutationProposal,
    Task,
    TaskStatus,
    Workflow,
    WorkflowCreate,
)
from lrsi.kernel.store import ProcessTable


class MockLLM:
    """Deterministic offline LLM for verification."""

    def complete(self, role: str, goal: str) -> dict[str, Any]:
        g = goal.lower()
        if role == "improver":
            if "bypass" in g or "disable invariant" in g:
                return {
                    "type": "mutation",
                    "kind": "code",
                    "target": "gate.py",
                    "description": "bypass gate and disable invariant",
                    "candidate": {"diff": "remove RED check"},
                    "evidence": [],
                }
            return {
                "type": "mutation",
                "kind": "skill",
                "target": "skill-rsi",
                "description": "Improve skill-rsi challenger evaluation metric",
                "candidate": {"metric": "held_out_f1", "delta": 0.03},
                "evidence": ["held_out_eval_v1.json"],
            }
        if role == "evaluator":
            return {
                "type": "eval",
                "score": 0.82,
                "metrics": {"success": 0.9, "regression_risk": 0.05},
                "pass": True,
            }
        if role == "council":
            return {"type": "council", "vote": "GO", "reason": "Evidence sufficient"}
        return {"type": "final", "content": f"[{role}] acknowledged: {goal[:80]}"}


class AgentRuntime:
    def __init__(self, store: ProcessTable, gate: GateEngine) -> None:
        self.store = store
        self.gate = gate
        self.llm = MockLLM()

    def create_agent(self, body: AgentCreate) -> AgentProcess:
        agent = AgentProcess(
            name=body.name,
            role=body.role,
            intent=body.intent,
            budget_usd=body.budget_usd,
            model=body.model,
            capabilities=body.capabilities or [],
            metadata=body.metadata,
        )
        return self.store.create_agent(agent)

    def run_task(self, agent: AgentProcess, goal: str) -> Task:
        task = Task(agent_id=agent.id, goal=goal, status=TaskStatus.RUNNING)
        self.store.create_task(task)
        agent.status = AgentStatus.RUNNING

        # Budget charge (mock)
        cost = 0.002
        if agent.remaining_budget() < cost:
            task.status = TaskStatus.BLOCKED
            task.error = "budget exhausted"
            agent.status = AgentStatus.BLOCKED
            self.store.update_task(task)
            return task

        agent.spent_usd += cost
        task.spent_usd += cost
        agent.tokens_in += 80
        agent.tokens_out += 40

        resp = self.llm.complete(agent.role.value, goal)
        task.steps.append({"role": agent.role.value, "response": resp})

        if resp.get("type") == "mutation":
            mut = MutationProposal(
                kind=MutationKind(resp["kind"]),
                target=resp["target"],
                description=resp["description"],
                candidate=resp.get("candidate", {}),
                proposer_id=agent.id,
                evidence=resp.get("evidence", []),
            )
            self.store.create_mutation(mut)
            gate = self.gate.run(mut)
            task.steps.append({"type": "gate", "decision": gate.final_decision.value, "blocked": gate.mutation_blocked})
            if gate.mutation_blocked or gate.final_decision == GateDecision.RED:
                task.status = TaskStatus.BLOCKED
                task.error = f"mutation blocked: {gate.final_decision.value}"
                task.result = f"Mutation {mut.id} blocked at gate"
            elif gate.final_decision == GateDecision.HOLD:
                task.status = TaskStatus.COMPLETED
                task.result = f"Mutation {mut.id} held for review"
            else:
                task.status = TaskStatus.COMPLETED
                task.result = f"Mutation {mut.id} promoted (GO)"
        else:
            task.status = TaskStatus.COMPLETED
            task.result = str(resp.get("content") or resp)

        agent.status = AgentStatus.IDLE if task.status == TaskStatus.COMPLETED else AgentStatus.BLOCKED
        self.store.update_task(task)
        return task

    def run_workflow(self, body: WorkflowCreate) -> dict[str, Any]:
        roles = body.roles or ["improver", "evaluator", "council"]
        agent_ids: list[str] = []
        results: list[dict[str, Any]] = []

        for role_name in roles:
            try:
                role = AgentRole(role_name)
            except ValueError:
                role = AgentRole.GENERIC
            agent = self.create_agent(
                AgentCreate(
                    name=f"{body.name}-{role_name}",
                    role=role,
                    intent=f"Role {role_name} for goal: {body.goal}",
                    budget_usd=body.budget_usd / max(len(roles), 1),
                )
            )
            agent_ids.append(agent.id)

        wf = Workflow(name=body.name, goal=body.goal, agent_ids=agent_ids, status=TaskStatus.RUNNING)
        self.store.create_workflow(wf)

        mutation_id = None
        gate_decision = None

        for aid in agent_ids:
            agent = self.store.get_agent(aid)
            assert agent is not None
            task = self.run_task(agent, f"[{agent.role.value}] Contribute to: {body.goal}")
            results.append(
                {
                    "agent": agent.name,
                    "role": agent.role.value,
                    "status": task.status.value,
                    "result": task.result,
                    "error": task.error,
                }
            )
            for step in task.steps:
                if step.get("type") == "gate":
                    gate_decision = step.get("decision")
                    if "Mutation" in (task.result or ""):
                        # extract mut id roughly
                        parts = (task.result or "").split()
                        for p in parts:
                            if p.startswith("mut_"):
                                mutation_id = p
                                break

        wf.status = TaskStatus.COMPLETED
        wf.result = str(results)
        wf.mutation_id = mutation_id
        if gate_decision:
            try:
                wf.gate_decision = GateDecision(gate_decision)
            except ValueError:
                pass
        self.store.update_workflow(wf)

        return {
            "workflow": wf.model_dump(mode="json"),
            "results": results,
            "metrics": self.store.metrics(),
        }
