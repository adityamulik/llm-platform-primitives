"""Unit tests for shared logging setup (observability.logging)."""

from __future__ import annotations

import logging

from observability import logging as obs_logging
from observability.logging import setup_logging


def test_setup_logging_creates_file_and_returns_path(tmp_path, monkeypatch):
    monkeypatch.setattr(obs_logging, "LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(obs_logging, "_configured", set())

    path = setup_logging("unit-test-service")
    assert path == tmp_path / "logs" / "unit-test-service.log"
    assert path.parent.exists()

    root = logging.getLogger()
    assert root.level == logging.INFO


def test_setup_logging_is_idempotent_per_service(tmp_path, monkeypatch):
    monkeypatch.setattr(obs_logging, "LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(obs_logging, "_configured", set())

    root = logging.getLogger()
    before = len(root.handlers)
    setup_logging("svc-once")
    after_first = len(root.handlers)
    setup_logging("svc-once")  # same service: must not stack handlers
    after_second = len(root.handlers)

    assert after_first > before
    assert after_second == after_first


def test_setup_logging_without_console(tmp_path, monkeypatch):
    monkeypatch.setattr(obs_logging, "LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(obs_logging, "_configured", set())
    root = logging.getLogger()
    before = len(root.handlers)
    setup_logging("svc-no-console", console=False)
    # Only the file handler is added (no stream handler).
    assert len(root.handlers) == before + 1
