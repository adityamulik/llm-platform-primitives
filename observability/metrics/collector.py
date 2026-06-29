"""Per-user runtime metrics: tokens, cost, success/error counts, latency.

A single in-process :class:`MetricsCollector` aggregates counters keyed by
user id. The current user is carried on a context var (set by the gateway at
request start, mirroring ``agent.set_request_auth``) so the agent's model
callbacks can attribute token usage without threading the user id through every
call.

In-memory only — counters reset on process restart. Expose ``snapshot()`` via an
HTTP endpoint to scrape, or swap the body of the ``record_*`` methods for a
push to Prometheus/StatsD without touching the call sites.
"""

from __future__ import annotations

import contextvars
import threading
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass

# Current authenticated user for the in-flight request. Default keeps metrics
# attributable even if the gateway forgets to set it.
_current_user: contextvars.ContextVar[str] = contextvars.ContextVar(
    "current_user", default="anonymous"
)


def set_current_user(user_id: str | None) -> None:
    """Record the authenticated user for the current request/context."""
    _current_user.set(user_id or "anonymous")


def get_current_user() -> str:
    """The user the current context's metrics should be attributed to."""
    return _current_user.get()


@dataclass
class UserMetrics:
    """Cumulative counters for a single user."""

    user_id: str
    requests: int = 0
    successes: int = 0
    errors: int = 0
    hallucinations: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_cost_usd: float = 0.0
    # Sum of per-request wall-clock latency; divided by ``requests`` for the avg.
    total_latency_s: float = 0.0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def avg_latency_s(self) -> float:
        return self.total_latency_s / self.requests if self.requests else 0.0

    @property
    def success_rate(self) -> float:
        return self.successes / self.requests if self.requests else 0.0


class MetricsCollector:
    """Thread-safe aggregator of per-user metrics."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._users: dict[str, UserMetrics] = {}

    def _bucket(self, user_id: str) -> UserMetrics:
        # Caller must hold the lock.
        m = self._users.get(user_id)
        if m is None:
            m = UserMetrics(user_id=user_id)
            self._users[user_id] = m
        return m

    def record_tokens(
        self,
        user_id: str,
        *,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float = 0.0,
    ) -> None:
        """Add one model call's token usage to the user's totals."""
        with self._lock:
            m = self._bucket(user_id)
            m.input_tokens += input_tokens
            m.output_tokens += output_tokens
            m.total_cost_usd += cost_usd

    def record_request(
        self, user_id: str, *, success: bool, latency_s: float
    ) -> None:
        """Record one completed request (success or failure) and its latency."""
        with self._lock:
            m = self._bucket(user_id)
            m.requests += 1
            if success:
                m.successes += 1
            else:
                m.errors += 1
            m.total_latency_s += latency_s

    def record_hallucination(self, user_id: str) -> None:
        """Count a schema-validation failure (model produced invalid output)."""
        with self._lock:
            self._bucket(user_id).hallucinations += 1

    @contextmanager
    def track_request(self, user_id: str):
        """Time a request body and record success/error + latency on exit.

        A normal exit (including ``return``) counts as success; any exception
        counts as an error, then re-raises so callers handle it as usual.
        """
        start = time.perf_counter()
        try:
            yield
        except Exception:
            self.record_request(
                user_id, success=False, latency_s=time.perf_counter() - start
            )
            raise
        else:
            self.record_request(
                user_id, success=True, latency_s=time.perf_counter() - start
            )

    def snapshot(self, user_id: str | None = None) -> dict:
        """Point-in-time copy of the counters, JSON-serializable.

        Pass ``user_id`` for one user, or omit for all users.
        """
        with self._lock:
            if user_id is not None:
                m = self._users.get(user_id)
                return _as_dict(m) if m else {}
            return {uid: _as_dict(m) for uid, m in self._users.items()}


def _as_dict(m: UserMetrics) -> dict:
    d = asdict(m)
    d["total_tokens"] = m.total_tokens
    d["avg_latency_s"] = round(m.avg_latency_s, 6)
    d["success_rate"] = round(m.success_rate, 4)
    return d


# Process-wide singleton.
metrics = MetricsCollector()
