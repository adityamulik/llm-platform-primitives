"""Unit tests for the specialist output schemas (app/model.py)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.model import (
    ApproachComparison,
    CodebaseOutput,
    CodeFinding,
    Confidence,
    DocsOutput,
    DocSource,
    ExecutionOutput,
    ExecutionStatus,
    ResearchOutput,
    Severity,
)


def test_docs_output_minimal():
    out = DocsOutput(answer="a", library_name="FastAPI", grounded=True)
    assert out.version is None
    assert out.sources == []
    assert out.out_of_scope is False


def test_docs_output_with_sources():
    out = DocsOutput(
        answer="a",
        library_name="Next.js",
        version="14",
        sources=[DocSource(library_id="/vercel/next.js", topic="routing")],
        grounded=True,
    )
    assert out.sources[0].topic == "routing"


def test_docs_output_requires_grounded():
    with pytest.raises(ValidationError):
        DocsOutput(answer="a", library_name="x")


def test_codebase_output_and_severity_enum():
    finding = CodeFinding(
        title="SQL injection",
        severity=Severity.critical,
        location="db.py:10",
        recommendation="Parameterize the query",
    )
    out = CodebaseOutput(
        summary="ok",
        findings=[finding],
        design_patterns=["singleton"],
        maintainability_score=80,
    )
    assert out.findings[0].severity == "critical"
    assert out.maintainability_score == 80


def test_codebase_maintainability_score_bounds():
    with pytest.raises(ValidationError):
        CodebaseOutput(summary="s", maintainability_score=101)
    with pytest.raises(ValidationError):
        CodebaseOutput(summary="s", maintainability_score=-1)


def test_codebase_invalid_severity():
    with pytest.raises(ValidationError):
        CodeFinding(title="t", severity="catastrophic", recommendation="r")


def test_research_output():
    out = ResearchOutput(
        summary="s",
        key_findings=["f1"],
        approaches_compared=[ApproachComparison(name="A", pros=["fast"], cons=["risky"])],
        recommendation="use A",
        confidence=Confidence.high,
        sources=["src1"],
    )
    assert out.confidence == "high"
    assert out.approaches_compared[0].name == "A"


def test_execution_output_status_enum():
    out = ExecutionOutput(summary="done", status=ExecutionStatus.success)
    assert out.status == "success"
    assert out.steps_taken == []
    assert out.issues == []


def test_execution_output_invalid_status():
    with pytest.raises(ValidationError):
        ExecutionOutput(summary="s", status="maybe")
