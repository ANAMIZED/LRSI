# LRSI

[![CI](https://github.com/ANAMIZED/LRSI/actions/workflows/ci.yml/badge.svg)](https://github.com/ANAMIZED/LRSI/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**LRSI (Local Recursive Self-Improvement) — Autonomous Agentic Operating System**

LRSI is achievable as a sovereign, closed-loop system on dual Blackwell hardware (RTX 5090 + RTX 6000-series). The foundation is the real, open **LRSI Runtime Core** ([marcuszimmermann365/IRSI](https://github.com/marcuszimmermann365/IRSI), v13.3.0), a phase-based, event-sourced, fail-closed research runtime explicitly designed for controlled self-modification, interruptibility, auditability, human-review binding, and replayable decisions.

It is **not** a complete production OS or certified alignment solution. It is the hardened governance kernel every serious local RSI system needs. The rest of the stack (model serving, outer improver, executable gym, hot-swappable harness, bounded weight updates) is built around it so that *every* mutation of code, skills, prompts, harness, evaluators, or (bounded) model weights is forced through the same fail-closed boundary and append-only event trail.

A senior engineer who has never seen this repository can, using **only** the source code and this `README.md`:

1. Stand up the LRSI Runtime Core and verify the self-modification boundary
2. Wire local model serving (vLLM / SGLang) on dual GPUs
3. Run a concrete improvement loop under the LRSI gates
4. Expand under the same invariants

No prior context or tribal knowledge required.

## Quick Start

```bash
# 1. Clone and verify the LRSI Runtime Core (foundation)
git clone https://github.com/marcuszimmermann365/IRSI.git
cd IRSI
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"          # or ".[live]" for real LLM support
python runner.py --iterations 3 --storage-path run_log.json --memory-path memory_store.json
python -m pytest -q -rs
python scripts/check_phase_event_coverage.py --run-sample --iterations 3
```

Then return to this repo and follow the phased roadmap below.

Default mode for the outer stack is **offline / mock** where possible. Point live endpoints at local vLLM/SGLang.

## Core of LRSI Runtime Core (v13.3.0)

- **Phase pipeline** (high-level): Review Mode → Mutation → PreProposalAdversarial → DGM Precheck → Evaluation → Council → Hold Logic → Human Review → Erosion & Human Coupling → Attractor Analysis → Adversarial → DGM Postcheck → Final Gate → Apply/Reject → Memory Consolidation → Post-decision Accounting → Observability → Persistence.
- **Self-modification boundary** (the critical segment): Mutation → PreProposalAdversarialPhase (hard kill-switch) → DGMPrecheckPhase → downstream governance → Final Gate. A `RED` decision in PreProposalAdversarial is terminal (`mutation_blocked=true`). Multiple defense-in-depth checks and 11 central invariants (in `invariants.py`) prevent bypasses, HOLD-state mutations, Council RED softening into GO, event-chain breaks, etc.
- **Event sourcing**: Every meaningful `PhaseResult` emits a `phase.result` event into an append-only, hash-chained JSONL store (`*.events.jsonl`). `run_log.json` is only a materialized compatibility view. Full replay, projection, and verification are first-class. Production mode can require signed events + WORM/external sinks.
- **LLM integration**: `LLMClient` supports `mock` / `fixture` / `live` modes. Live mode is OpenAI-compatible (base_url, API key, model, temperature, etc.). This is the seam for pointing at a local vLLM/SGLang endpoint.
- License: Apache 2.0. It is research-oriented; treat the invariant set as a strong engineering control layer, not a mathematical proof.

All state (events, memory, skills, checkpoints) lives on local fast storage. The runtime is deliberately interruptible and fail-closed.

## Hardware Fit (2026)

RTX 5090 (32 GB GDDR7, ~1.79 TB/s, Blackwell Tensor Cores) + RTX 6000-series (Ada 48 GB or PRO Blackwell 96 GB GDDR7 ECC) is excellent. Unsloth, vLLM, and SGLang have explicit Blackwell / RTX 50-series / RTX PRO 6000 support (CUDA 12.8+, native FP4/NVFP4, optimized kernels, FlashAttention variants). Typical allocation: primary inference/agent on the 5090; evaluation, training sandboxes, or larger-batch work on the 6000. Multi-process, tensor/pipeline parallelism, and continuous batching all work.

## High-Level Architecture for an Agentic OS

```
┌─────────────────────────────────────────────────────────────┐
│                 LRSI Runtime Core (Governance Kernel)        │
│  Mutation → PreProposalAdversarial → DGM Precheck → ...     │
│  → Final Gate → Apply/Reject → Memory Consolidation         │
│  Event-sourced audit + fail-closed kill-switches + invariants│
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│              Hot-Swappable Harness (Cordis-style)            │
│  Tools, skills, memory, loops, sandboxes, model adapters    │
│  as reversible plugins (temporal + spatial composability)   │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│              Outer RSI / Improver Agent Loop                 │
│  Observe → Propose bounded mutation (skill/prompt/code/     │
│  harness/ops) → Ground in ontology/research → Submit to LRSI│
│  Local LLM (vLLM/SGLang)                                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│         Executable Feedback + Evaluation Gym                 │
│  Isolated sandboxes, multi-metric scoring, red-team checks, │
│  OpenMLE-Gym-style tasks, parallel across both GPUs         │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│      Model / Skill / Operator Evolution (evidence-gated)     │
│  QLoRA/Unsloth, Skill-RSI loops, OpenMLE operators,         │
│  checkpoints, operator evolution                            │
└─────────────────────────────────────────────────────────────┘
```

## Concrete Build Roadmap

**Phase 0 – Foundation (1–2 days)**  
Clone and verify LRSI exactly as above. Confirm RED decisions are terminal, event hash-chain integrity, and the self-modification boundary. Set up multi-GPU (CUDA 12.8+, NCCL if needed). Optional Docker isolation for later sandboxes.

**Phase 1 – Local Model Serving**  
Serve a strong open-weight model (Qwen3.x 30–35B-class MoE, Llama-class 70B Q4/FP8/NVFP4, or 2026 equivalents) with vLLM or SGLang. Enable FP4/NVFP4, continuous batching, FlashAttention. Expose an OpenAI-compatible endpoint. Point LRSI’s `LLMClient` (and any outer agent) at it via `LLM_BASE_URL` + key. Allocate 5090 primarily to inference; 6000 to heavier jobs.

**Phase 2 – Core Agent + Improvement Operators + Harness**  
- Extend or wrap LRSI’s MutationPhase so it can accept richer candidates (skill definitions, code diffs, harness config, routing logic). Keep one-variable-at-a-time discipline early.
- Build a thin outer improver agent (custom loop or LangGraph) that observes outcomes/failures, proposes bounded mutations, and grounds them in domain research/ontology.
- Adopt **Skill-RSI**-style loops for skill improvement: research → ontology → controlled challenger vs champion → evidence-based promotion. All proposals still go through LRSI gates.
- Make the agent runtime itself hot-swappable using **DeepSeek Harness / Cordis** principles (or a lightweight Python equivalent): tools, skills, memory backends, loops, sandboxes, and model adapters as plugins with reversible effects (temporal composability = clean unload/rollback; spatial = declared reactive dependencies). This prevents the classic “agent kills its own recovery path” failure mode and enables continuous evolution without restarts.

**Phase 3 – Executable Gym & Evaluation**  
- Isolated sandboxes (Docker / Firecracker / process isolation + resource limits).
- Multi-metric scoring: task success, efficiency, regression risk, safety invariants, red-team checks.
- Parallel evaluation jobs across both GPUs.
- Strong inspiration from **OpenMLE-Gym** (executable MLE tasks with structured feedback) and the broader OpenRSI stack (OpenMLE-ERL for learning Draft/Improve/Debug/Crossover operators, OpenMLE-Evo for long-horizon search). Frontis-MA1 (35B) is a concrete post-trained meta-evolution agent that can be adapted or used as a reference.
- Require independent evidence (not self-report) before any promotion.

**Phase 4 – Closed Recursive Loop under LRSI Gates**  
Wire every proposed mutation through the full LRSI pipeline. Promote only when:
- Pre-proposal adversarial is not RED,
- Evaluation shows clear improvement on held-out metrics,
- Final gate (+ optional early human review) passes.
On promotion: update skill library / harness / memory; optionally trigger a QLoRA update of the improver itself via Unsloth (Blackwell-optimized) on the 6000 while inference continues. Everything is recorded in the append-only event stream for full replay and audit.

**Phase 5 – Meta & Scaling**  
Higher-level loops that improve the improver (operators, evaluation criteria, gating logic, even parts of the harness) — still under the same LRSI gates. Continuous background cycles with backoff. Safe improvements apply autonomously; risky ones hold for review. Optional later federation of summaries only (weights and raw data stay local).

## Recommended Tech Stack (Local-First, 2026)

| Layer              | Recommendation                                      |
|--------------------|-----------------------------------------------------|
| Governance/Safety  | LRSI Runtime Core v13.3.0                           |
| Inference          | vLLM or SGLang (Blackwell-tuned, OpenAI-compatible) |
| Fine-tuning        | Unsloth + PEFT/TRL (explicit RTX 50 / PRO 6000)     |
| Agent orchestration| Custom + LangGraph or lightweight loop; Cordis-inspired plugins |
| Skill evolution    | Skill-RSI patterns                                  |
| Executable gym     | OpenMLE-Gym style + custom sandboxes                |
| Sandboxing         | Docker / Firecracker + resource limits              |
| Storage            | Local JSONL event store + SQLite/Postgres views + vector store |
| Monitoring         | LRSI structured logs + nvidia-smi / DCGM            |

## Realistic Expectations

- Strong Level-3 / early Level-4 style RSI (harness, skill, prompt, and code self-improvement with grounded evaluation) is practical today on this hardware at high throughput.
- Bounded model improvement (QLoRA of the improver, operator evolution) is practical.
- Full open-ended architecture redesign + continuous frontier-scale pre-training remains FLOPs-constrained, but the system can prepare the ground and run smaller-scale architecture/search experiments.
- Safety is first-class because every self-modification attempt is forced through the LRSI fail-closed boundary and event-sourced audit trail. The Cordis-style reversible plugin model further reduces irreversible damage risk.

## Practical Starting Sequence

1. Stand up LRSI Runtime Core and verify the self-modification boundary and event chain.
2. Stand up a local vLLM/SGLang server on the dual GPUs and wire LRSI’s LLMClient to it.
3. Implement one concrete improvement loop (e.g., Skill-RSI style for a single skill family, or simple prompt/policy mutations) that submits candidates exclusively through LRSI.
4. Add sandboxed evaluation and multi-metric scoring.
5. Expand the mutation surface and add meta-loops only under the same gates.
6. Gradually introduce hot-swappable harness components with reversible effects.

This produces a true end-to-end local LRSI system that functions as an Autonomous Agentic Operating System: sovereign, auditable, interruptible, and capable of compounding improvements on exactly the GPUs you have. The LRSI kernel provides the non-negotiable safety and audit substrate; the surrounding layers supply the agentic power and evolutionary surface. Start narrow and evidence-gated; expand under the same invariants.

## Surfaces

| Surface | Entry |
|---------|-------|
| **LRSI Runtime Core** | External: [marcuszimmermann365/IRSI](https://github.com/marcuszimmermann365/IRSI) |
| Outer improver / harness | `src/lrsi/` (scaffolding) |
| Skills | `skills/*/SKILL.md` |
| AGENTS.md | Coding-agent contract at repo root |
| Verify | `bash scripts/verify.sh` |

## Verify contract

```bash
bash scripts/verify.sh
```

Covers foundation checks, structure, skills, and AGENTS.md. Expand as the outer stack matures.

## Design principles

1. Fail closed
2. Every mutation through the LRSI boundary
3. Event-sourced audit trail
4. Evidence-gated promotion (no self-report)
5. Reversible harness plugins (temporal + spatial composability)
6. Local-first, sovereign, interruptible

## License

Apache-2.0
