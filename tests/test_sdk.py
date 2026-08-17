"""SDK client tests."""

from lrsi.kernel.models import AgentCreate, AgentRole, WorkflowCreate
from lrsi.runtime_factory import reset_runtime
from lrsi.sdk import LRSIClient


def setup_function():
    reset_runtime()


def test_sdk_health_and_metrics():
    with LRSIClient() as c:
        h = c.health()
        assert h["status"] == "ok"
        assert h["chain_ok"] is True
        m = c.metrics()
        assert "agents_created" in m


def test_sdk_agent_lifecycle():
    with LRSIClient() as c:
        a = c.create_agent(
            AgentCreate(name="sdk-a", role=AgentRole.EVALUATOR, intent="Score held-out", budget_usd=0.3)
        )
        assert a.id.startswith("agt_")
        listed = c.list_agents()
        assert any(x.id == a.id for x in listed)
        got = c.get_agent(a.id)
        assert got.name == "sdk-a"


def test_sdk_workflow():
    with LRSIClient() as c:
        out = c.create_workflow(
            WorkflowCreate(
                name="sdk-wf",
                goal="Safe skill improvement",
                roles=["improver", "evaluator", "council"],
            )
        )
        assert out["workflow"]["status"] == "completed"
        assert c.verify_chain()
