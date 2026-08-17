"""Smoke tests for LRSI scaffolding."""

from pathlib import Path


def test_package_version():
    import lrsi
    assert lrsi.__version__ == "0.1.0"


def test_skills_exist():
    root = Path(__file__).resolve().parents[1]
    for name in ("governance-audit", "skill-rsi", "harness-plugin"):
        assert (root / "skills" / name / "SKILL.md").is_file()


def test_agents_md_exists():
    root = Path(__file__).resolve().parents[1]
    assert (root / "AGENTS.md").is_file()
