"""Core domain models for LRSI outer stack."""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:12]}"


def hash_event(prev_hash: str, payload: str) -> str:
    return hashlib.sha256(f"{prev_hash}:{payload}".encode()).hexdigest()


class AgentRole(str, Enum):
    IMPROVER = "improver"
    EVALUATOR = "evaluator"
    COUNCIL = "council"
    RESEARCHER = "researcher"
    HARNESS = "harness"
    GENERIC = "generic"


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    HOLD = "hold"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class GateDecision(str, Enum):
    GO = "GO"
    HOLD = "HOLD"
    RED = "RED"


class MutationKind(str, Enum):
    SKILL = "skill"
    PROMPT = "prompt"
    CODE = "code"
    HARNESS = "harness"
    WEIGHTS = "weights"
    OPERATOR = "operator"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class AgentCreate(BaseModel):
    name: str
    role: AgentRole = AgentRole.GENERIC
    intent: str
    budget_usd: float = 1.0
    model: str = "mock-local"
    capabilities: list[str] = Field(default_factory=lambda: ["propose_mutation", "evaluate", "memory_read"])
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentProcess(BaseModel):
    id: str = Field(default_factory=lambda: new_id("agt_"))
    name: str
    role: AgentRole = AgentRole.GENERIC
    intent: str
    status: AgentStatus = AgentStatus.IDLE
    budget_usd: float
    spent_usd: float = 0.0
    tokens_in: int = 0
    tokens_out: int = 0
    model: str
    capabilities: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def remaining_budget(self) -> float:
        return max(0.0, self.budget_usd - self.spent_usd)


class MutationProposal(BaseModel):
    id: str = Field(default_factory=lambda: new_id("mut_"))
    kind: MutationKind
    target: str
    description: str
    candidate: dict[str, Any] = Field(default_factory=dict)
    proposer_id: str | None = None
    evidence: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)


class PhaseResult(BaseModel):
    phase: str
    decision: GateDecision
    reason: str
    data: dict[str, Any] = Field(default_factory=dict)
    mutation_blocked: bool = False


class GateRecord(BaseModel):
    id: str = Field(default_factory=lambda: new_id("gate_"))
    mutation_id: str
    phases: list[PhaseResult] = Field(default_factory=list)
    final_decision: GateDecision = GateDecision.HOLD
    mutation_blocked: bool = False
    event_hash: str = ""
    created_at: datetime = Field(default_factory=utcnow)


class AuditEvent(BaseModel):
    id: str = Field(default_factory=lambda: new_id("aud_"))
    kind: str
    decision: str
    reason: str
    agent_id: str | None = None
    mutation_id: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    prev_hash: str = ""
    event_hash: str = ""
    timestamp: datetime = Field(default_factory=utcnow)


class Task(BaseModel):
    id: str = Field(default_factory=lambda: new_id("tsk_"))
    agent_id: str
    goal: str
    status: TaskStatus = TaskStatus.PENDING
    result: str | None = None
    error: str | None = None
    spent_usd: float = 0.0
    steps: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class WorkflowCreate(BaseModel):
    name: str
    goal: str
    roles: list[str] = Field(default_factory=lambda: ["improver", "evaluator", "council"])
    budget_usd: float = 2.0


class Workflow(BaseModel):
    id: str = Field(default_factory=lambda: new_id("wf_"))
    name: str
    goal: str
    agent_ids: list[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: str | None = None
    mutation_id: str | None = None
    gate_decision: GateDecision | None = None
    created_at: datetime = Field(default_factory=utcnow)
