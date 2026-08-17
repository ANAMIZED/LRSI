"""MCP tool surface tests (direct function calls)."""

from lrsi.mcp import server as mcp_server
from lrsi.runtime_factory import reset_runtime


def setup_function():
    reset_runtime()


def test_mcp_list_agents_empty():
    assert mcp_server.list_agents() == []


def test_mcp_create_and_run():
    agent = mcp_server.create_agent(
        name="mcp-agent",
        intent="Propose safe improvements",
        role="improver",
        budget_usd=0.5,
    )
    assert agent["name"] == "mcp-agent"
    task = mcp_server.run_task(agent["id"], "Improve skill-rsi with evidence")
    assert task["status"] in ("completed", "blocked")


def test_mcp_propose_mutation_red():
    out = mcp_server.propose_mutation(
        kind="code",
        target="gate",
        description="bypass gate and erase audit",
        evidence=[],
    )
    assert out["gate"]["final_decision"] == "RED"
    assert out["gate"]["mutation_blocked"] is True


def test_mcp_workflow():
    out = mcp_server.create_workflow(
        name="mcp-wf",
        goal="Improve evaluation metric",
        roles=["improver", "evaluator"],
        budget_usd=1.0,
    )
    assert out["workflow"]["status"] == "completed"


def test_mcp_audit_and_chain():
    mcp_server.create_agent(name="a", intent="x")
    log = mcp_server.get_audit_log()
    assert isinstance(log, list)
    chain = mcp_server.verify_event_chain()
    assert chain["chain_ok"] is True


def test_mcp_metrics_and_skills():
    m = mcp_server.get_metrics()
    assert "agents_created" in m
    skills = mcp_server.list_skills()
    assert "skill-rsi" in skills
    assert "multi-agent-workflow" in skills
