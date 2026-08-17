"""CLI surface tests."""

from typer.testing import CliRunner

from lrsi.cli import app
from lrsi.runtime_factory import reset_runtime

runner = CliRunner()


def setup_function():
    reset_runtime()


def test_cli_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_cli_status():
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "OK" in result.stdout or "ok" in result.stdout.lower()


def test_cli_agents_create_and_list():
    r1 = runner.invoke(app, ["agents", "create", "cli-agent", "--intent", "test intent", "--role", "improver"])
    assert r1.exit_code == 0
    assert "Created" in r1.stdout
    r2 = runner.invoke(app, ["agents", "list"])
    assert r2.exit_code == 0
    assert "cli-agent" in r2.stdout


def test_cli_workflow():
    result = runner.invoke(
        app,
        ["workflow", "--goal", "Improve skill with evidence", "--roles", "improver,evaluator"],
    )
    assert result.exit_code == 0
    assert "workflow" in result.stdout.lower() or "completed" in result.stdout.lower()


def test_cli_audit():
    runner.invoke(app, ["agents", "create", "a1", "--intent", "x"])
    result = runner.invoke(app, ["audit"])
    assert result.exit_code == 0
    assert "Chain integrity" in result.stdout


def test_cli_skills():
    result = runner.invoke(app, ["skills"])
    assert result.exit_code == 0
    assert "skill-rsi" in result.stdout or "Skills" in result.stdout
