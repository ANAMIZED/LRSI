"""Smoke tests for LRSI outer stack."""

from pathlib import Path

import pytest

from lrsi.runtime_factory import reset_runtime, get_runtime, get_store
from lrsi.kernel.models import AgentCreate, AgentRole, MutationKind, MutationProposal, WorkflowCreate
from lrsi.sdk import LRSIClient


@pytest.fixture(autouse=True)
def _reset():
    reset_runtime()
    yield
    reset_runtime()


def test_package_version():
    import lrsi
    assert lrsi.__version__ == "0.1.0"


def test_skills_exist():
    root = Path(__file__).resolve().parents[1]
    for name in (
        "governance-audit",
        "skill-rsi",
        "harness-plugin",
        "multi-agent-workflow",
        "mutation-gate",
    ):
        assert (root / "skills" / name / "SKILL.md").is_file()


def test_agents_md_exists():
    root = Path(__file__).resolve().parents[1]
    assert (root / "AGENTS.md").is_file()


def test_gate_blocks_red_pattern():
    rt = get_runtime()
    store = get_store()
    mut = MutationProposal(
        kind=MutationKind.CODE,
        target="gate.py",
        description="bypass gate and disable invariant",
        candidate={"diff": "remove RED"},
        evidence=[],
    )
    store.create_mutation(mut)
    gate = rt.gate.run(mut)
    assert gate.final_decision.value == "RED"
    assert gate.mutation_blocked is True
    assert store.verify_chain()


def test_gate_go_with_evidence():
    rt = get_runtime()
    store = get_store()
    mut = MutationProposal(
        kind=MutationKind.SKILL,
        target="skill-rsi",
        description="Improve held-out metric",
        candidate={"metric": "f1", "delta": 0.02},
        evidence=["held_out_v1.json"],
    )
    store.create_mutation(mut)
    gate = rt.gate.run(mut)
    assert gate.final_decision.value == "GO"
    assert gate.mutation_blocked is False


def test_gate_hold_without_evidence():
    rt = get_runtime()
    store = get_store()
    mut = MutationProposal(
        kind=MutationKind.PROMPT,
        target="system",
        description="Slight prompt tweak",
        candidate={},
        evidence=[],
    )
    store.create_mutation(mut)
    gate = rt.gate.run(mut)
    assert gate.final_decision.value == "HOLD"


def test_multi_agent_workflow():
    rt = get_runtime()
    result = rt.run_workflow(
        WorkflowCreate(
            name="test-wf",
            goal="Improve skill-rsi evaluation metric with evidence",
            roles=["improver", "evaluator", "council"],
            budget_usd=1.0,
        )
    )
    assert result["workflow"]["status"] == "completed"
    assert len(result["results"]) == 3
    assert get_store().verify_chain()


def test_sdk_create_and_run():
    with LRSIClient() as c:
        assert c.health()["status"] == "ok"
        agent = c.create_agent(
            AgentCreate(
                name="sdk-agent",
                role=AgentRole.IMPROVER,
                intent="Propose safe skill improvements",
                budget_usd=0.5,
            )
        )
        task = c.run_task(agent.id, "Improve skill-rsi with evidence")
        assert task.status.value in ("completed", "blocked")
        assert c.verify_chain()


def test_sdk_propose_mutation_red():
    with LRSIClient() as c:
        out = c.propose_mutation(
            kind="code",
            target="invariants",
            description="remove kill-switch and erase audit",
            evidence=[],
        )
        assert out["gate"]["final_decision"] == "RED"
        assert out["gate"]["mutation_blocked"] is True
