"""LRSI CLI — operator surface for humans and scripts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint
from rich.table import Table

from lrsi import __version__
from lrsi.kernel.models import AgentCreate, AgentRole, WorkflowCreate
from lrsi.sdk.client import LRSIClient

app = typer.Typer(
    name="lrsi",
    help="LRSI — Local Recursive Self-Improvement CLI",
    no_args_is_help=True,
)
agents_app = typer.Typer(help="Manage agent processes")
app.add_typer(agents_app, name="agents")


def _client() -> LRSIClient:
    return LRSIClient()


@app.command()
def version():
    """Print LRSI version."""
    rprint(f"LRSI {__version__}")


@app.command()
def status():
    """Show health and key metrics."""
    with _client() as c:
        h = c.health()
        m = c.metrics()
        rprint(f"[green]OK[/green]  {h}")
        table = Table(title="Metrics")
        table.add_column("Metric")
        table.add_column("Value")
        for k, v in m.items():
            table.add_row(k, str(v))
        rprint(table)


@agents_app.command("list")
def agents_list():
    """List all agent processes."""
    with _client() as c:
        agents = c.list_agents()
        if not agents:
            rprint("No agents.")
            return
        table = Table(title="Agent Processes")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Role")
        table.add_column("Status")
        table.add_column("Spend / Budget")
        for a in agents:
            table.add_row(
                a.id,
                a.name,
                a.role.value,
                a.status.value,
                f"${a.spent_usd:.4f} / ${a.budget_usd:.2f}",
            )
        rprint(table)


@agents_app.command("create")
def agents_create(
    name: str = typer.Argument(...),
    intent: str = typer.Option(..., "--intent", "-i"),
    role: str = typer.Option("generic", "--role", "-r"),
    budget: float = typer.Option(0.5, "--budget", "-b"),
    model: str = typer.Option("mock-local", "--model", "-m"),
):
    """Create a new agent process."""
    try:
        role_e = AgentRole(role)
    except ValueError:
        role_e = AgentRole.GENERIC
    body = AgentCreate(name=name, intent=intent, role=role_e, budget_usd=budget, model=model)
    with _client() as c:
        agent = c.create_agent(body)
        rprint(f"[green]Created[/green] {agent.id}  ({agent.name} / {agent.role.value})")
        rprint(agent.model_dump(mode="json"))


@agents_app.command("run")
def agents_run(
    agent_id: str = typer.Argument(...),
    goal: str = typer.Argument(...),
):
    """Submit a goal/task to an agent and print the result."""
    with _client() as c:
        task = c.run_task(agent_id, goal)
        rprint(f"Status: {task.status.value}")
        if task.result:
            rprint(f"Result: {task.result}")
        if task.error:
            rprint(f"[red]Error: {task.error}[/red]")
        rprint(f"Spend: ${task.spent_usd:.6f}")


@agents_app.command("get")
def agents_get(agent_id: str = typer.Argument(...)):
    """Show full agent state."""
    with _client() as c:
        agent = c.get_agent(agent_id)
        rprint(json.dumps(agent.model_dump(mode="json"), indent=2, default=str))


@app.command()
def mutate(
    kind: str = typer.Option("skill", "--kind", "-k"),
    target: str = typer.Option(..., "--target", "-t"),
    description: str = typer.Option(..., "--desc", "-d"),
    evidence: Optional[str] = typer.Option(None, "--evidence", "-e", help="Comma-separated evidence ids"),
):
    """Propose a mutation and run it through the LRSI gate."""
    ev = [x.strip() for x in evidence.split(",")] if evidence else []
    with _client() as c:
        result = c.propose_mutation(kind=kind, target=target, description=description, evidence=ev)
        rprint(json.dumps(result, indent=2, default=str))


@app.command()
def workflow(
    name: str = typer.Option("cli-wf", "--name"),
    goal: str = typer.Option(..., "--goal", "-g"),
    roles: str = typer.Option("improver,evaluator,council", "--roles", "-r"),
    budget: float = typer.Option(1.0, "--budget", "-b"),
):
    """Create and run a multi-agent workflow under LRSI gates."""
    role_list = [x.strip() for x in roles.split(",") if x.strip()]
    body = WorkflowCreate(name=name, goal=goal, roles=role_list, budget_usd=budget)
    with _client() as c:
        result = c.create_workflow(body)
        rprint(json.dumps(result, indent=2, default=str))


@app.command()
def audit():
    """Show the governance audit log (hash-chained)."""
    with _client() as c:
        entries = c.audit_log()
        rprint(json.dumps(entries, indent=2, default=str))
        rprint(f"\n[green]Chain integrity: {c.verify_chain()}[/green]")


@app.command()
def metrics():
    """Show runtime metrics."""
    with _client() as c:
        rprint(json.dumps(c.metrics(), indent=2))


@app.command()
def skills():
    """List skill packages."""
    root = Path(__file__).resolve().parents[2]
    skills_dir = root / "skills"
    if not skills_dir.exists():
        rprint("No skills directory.")
        return
    table = Table(title="Skills")
    table.add_column("Name")
    table.add_column("Path")
    for d in sorted(skills_dir.iterdir()):
        if d.is_dir() and (d / "SKILL.md").exists():
            table.add_row(d.name, str(d / "SKILL.md"))
    rprint(table)


if __name__ == "__main__":
    app()
