"""Structured output schemas for the specialist agents.

Each specialist returns a typed payload (enforced via LlmAgent.output_schema)
so the root coordinator — and any downstream consumer — gets predictable,
machine-readable results instead of free-form prose. Field descriptions are
sent to the model as part of controlled generation, so they double as
instructions; keep them specific.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


# --- Docs agent -------------------------------------------------------------
class DocSource(BaseModel):
    """A single documentation snippet the answer was grounded in."""

    library_id: str = Field(
        description="Context7-compatible library ID the docs were fetched from, "
        "e.g. '/vercel/next.js'."
    )
    topic: str | None = Field(
        default=None,
        description="Topic the docs were scoped to, e.g. 'routing', if one was used.",
    )


class DocsOutput(BaseModel):
    """Result of a grounded documentation lookup."""

    answer: str = Field(
        description="The answer, grounded entirely in the fetched documentation."
    )
    library_name: str = Field(
        description="Human-readable name of the library the answer is about, e.g. 'FastAPI'."
    )
    version: str | None = Field(
        default=None,
        description="Library version the documentation reflects, if known.",
    )
    sources: list[DocSource] = Field(
        default_factory=list,
        description="Documentation sources cited; empty only when nothing was fetched.",
    )
    grounded: bool = Field(
        description="True if every claim is backed by the fetched docs; "
        "False if the docs did not cover the question.",
    )
    out_of_scope: bool = Field(
        default=False,
        description="True if the request fell outside documentation lookup.",
    )


# --- Codebase agent ---------------------------------------------------------
class Severity(str, Enum):
    info = "info"
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class CodeFinding(BaseModel):
    """A single issue or observation about the analyzed code."""

    title: str = Field(description="Short summary of the finding.")
    severity: Severity = Field(description="Impact level of the finding.")
    location: str | None = Field(
        default=None,
        description="Where it applies, e.g. 'auth/session.py:42' or a function name.",
    )
    recommendation: str = Field(
        description="Concrete, actionable fix or improvement."
    )


class CodebaseOutput(BaseModel):
    """Result of a code analysis / review pass."""

    summary: str = Field(description="Overall assessment of the code reviewed.")
    findings: list[CodeFinding] = Field(
        default_factory=list,
        description="Issues, risks, or improvement opportunities found.",
    )
    design_patterns: list[str] = Field(
        default_factory=list,
        description="Notable design patterns or anti-patterns identified.",
    )
    maintainability_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Optional maintainability rating from 0 (poor) to 100 (excellent).",
    )


# --- Research agent ---------------------------------------------------------
class ApproachComparison(BaseModel):
    """One option weighed during research."""

    name: str = Field(description="Name of the approach, tool, or methodology.")
    pros: list[str] = Field(default_factory=list, description="Advantages.")
    cons: list[str] = Field(default_factory=list, description="Drawbacks.")


class Confidence(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ResearchOutput(BaseModel):
    """Result of a research and analysis task."""

    summary: str = Field(description="Concise synthesis of the research.")
    key_findings: list[str] = Field(
        default_factory=list,
        description="The most important, evidence-based findings.",
    )
    approaches_compared: list[ApproachComparison] = Field(
        default_factory=list,
        description="Options evaluated, with their trade-offs.",
    )
    recommendation: str = Field(
        description="The recommended course of action and why."
    )
    confidence: Confidence = Field(
        description="Confidence in the recommendation given the available evidence."
    )
    sources: list[str] = Field(
        default_factory=list,
        description="References or sources the findings were synthesized from.",
    )


# --- Execution agent --------------------------------------------------------
class ExecutionStatus(str, Enum):
    success = "success"
    partial = "partial"
    failed = "failed"


class ExecutionOutput(BaseModel):
    """Result of an implementation / execution task."""

    summary: str = Field(description="What was attempted and the outcome.")
    status: ExecutionStatus = Field(description="Overall result of the work.")
    steps_taken: list[str] = Field(
        default_factory=list,
        description="Ordered steps performed to complete the task.",
    )
    artifacts: list[str] = Field(
        default_factory=list,
        description="Files created/modified, commands run, or resources produced.",
    )
    issues: list[str] = Field(
        default_factory=list,
        description="Problems hit during execution; empty if none.",
    )
    next_steps: list[str] = Field(
        default_factory=list,
        description="Follow-up actions needed, e.g. when status is 'partial'.",
    )
