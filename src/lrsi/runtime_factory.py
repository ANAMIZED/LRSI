"""Shared in-process runtime factory for CLI, SDK, and MCP."""

from __future__ import annotations

from lrsi.agents.runtime import AgentRuntime
from lrsi.governance.gate import GateEngine
from lrsi.kernel.store import ProcessTable

_store: ProcessTable | None = None
_gate: GateEngine | None = None
_runtime: AgentRuntime | None = None


def get_store() -> ProcessTable:
    global _store
    if _store is None:
        _store = ProcessTable()
    return _store


def get_gate() -> GateEngine:
    global _gate
    if _gate is None:
        _gate = GateEngine(get_store())
    return _gate


def get_runtime() -> AgentRuntime:
    global _runtime
    if _runtime is None:
        _runtime = AgentRuntime(get_store(), get_gate())
    return _runtime


def reset_runtime() -> None:
    """Reset for tests."""
    global _store, _gate, _runtime
    _store = None
    _gate = None
    _runtime = None
