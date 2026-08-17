"""LRSI as an MCP Server.

Exposes Local Recursive Self-Improvement primitives as MCP tools so any
MCP-compatible client can create agents, propose mutations under the
fail-closed gate, run multi-agent workflows, and inspect the audit trail.
"""

from __future__ import annotations

from typing import Any

from lrsi.kernel.models import AgentCreate, AgentRole, WorkflowCreate
from lrsi.runtime_factory import get_runtime, get_store

# Prefer official mcp package; fall back to a minimal stub for environments without it
try:
    from mcp.server import MCPServer  # type: ignore

    mcp = MCPServer(
        "LRSI",
        instructions=(
            "You are connected to LRSI, a Local Recursive Self-Improvement "
            "Autonomous Agentic Operating System. Every mutation is forced through "
            "a fail-closed gate (PreProposalAdversarial → Final Gate). Prefer "
            "evidence-gated, reversible changes."
        ),
    )
    _HAS_MCP = True
except Exception:  # pragma: no cover
    _HAS_MCP = False

    class _Stub:
        def tool(self, *a, **k):
            def deco(fn):
                return fn

            return deco

        def run(self):
            raise RuntimeError("mcp package not installed")

    mcp = _Stub()  # type: ignore


def _rt():
    return get_runtime()


def _store():
    return get_store()


@mcp.tool()
def list_agents() -> list[dict[str, Any]]:
    """List all agent processes with role, status, spend, and budget."""
    return [a.model_dump(mode="json") for a in _store().list_agents()]


@mcp.tool()
def create_agent(
    name: str,
    intent: str,
    role: str = "generic",
    budget_usd: float = 0.5,
    capabilities: list[str] | None = None,
    model: str = "mock-local",
) -> dict[str, Any]:
    """Create a new agent process (improver / evaluator / council / …)."""
    try:
        role_e = AgentRole(role)
    except ValueError:
        role_e = AgentRole.GENERIC
    body = AgentCreate(
        name=name,
        intent=intent,
        role=role_e,
        budget_usd=budget_usd,
        model=model,
        capabilities=capabilities or ["propose_mutation", "evaluate"],
    )
    agent = _rt().create_agent(body)
    return agent.model_dump(mode="json")


@mcp.tool()
def run_task(agent_id: str, goal: str) -> dict[str, Any]:
    """Submit a goal to an agent. Mutations are automatically gated."""
    agent = _store().get_agent(agent_id)
    if not agent:
        return {"error": f"agent not found: {agent_id}"}
    task = _rt().run_task(agent, goal)
    return task.model_dump(mode="json")


@mcp.tool()
def propose_mutation(
    kind: str,
    target: str,
    description: str,
    evidence: list[str] | None = None,
    candidate: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Propose a mutation and run the full LRSI gate (PreProposalAdversarial → Final)."""
    from lrsi.kernel.models import MutationKind, MutationProposal

    mut = MutationProposal(
        kind=MutationKind(kind),
        target=target,
        description=description,
        candidate=candidate or {},
        evidence=evidence or [],
    )
    _store().create_mutation(mut)
    gate = _rt().gate.run(mut)
    return {
        "mutation": mut.model_dump(mode="json"),
        "gate": gate.model_dump(mode="json"),
    }


@mcp.tool()
def create_workflow(
    name: str,
    goal: str,
    roles: list[str] | None = None,
    budget_usd: float = 1.0,
) -> dict[str, Any]:
    """Run a multi-agent workflow (improver → evaluator → council) under LRSI gates."""
    body = WorkflowCreate(
        name=name,
        goal=goal,
        roles=roles or ["improver", "evaluator", "council"],
        budget_usd=budget_usd,
    )
    return _rt().run_workflow(body)


@mcp.tool()
def get_audit_log() -> list[dict[str, Any]]:
    """Return the append-only, hash-chained governance audit trail."""
    return _store().audit_log()


@mcp.tool()
def verify_event_chain() -> dict[str, Any]:
    """Verify integrity of the hash-chained audit trail."""
    ok = _store().verify_chain()
    return {"chain_ok": ok, "events": len(_store().audit)}


@mcp.tool()
def get_metrics() -> dict[str, float]:
    """Return LRSI outer-stack metrics."""
    return _store().metrics()


@mcp.tool()
def list_skills() -> list[str]:
    """List available skill package names."""
    from pathlib import Path

    root = Path(__file__).resolve().parents[3]
    skills_dir = root / "skills"
    if not skills_dir.exists():
        return []
    return sorted(d.name for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists())


def main() -> None:
    """Entry point for lrsi-mcp / stdio MCP server."""
    if not _HAS_MCP:
        raise SystemExit("Install the 'mcp' package to run the LRSI MCP server")
    mcp.run()


if __name__ == "__main__":
    main()
