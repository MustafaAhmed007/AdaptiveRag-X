from dataclasses import dataclass, field
from time import perf_counter
from uuid import uuid4


@dataclass
class Trace:
    strategy: str
    trace_id: str = field(default_factory=lambda: str(uuid4()))
    started: float = field(default_factory=perf_counter)
    events: list[dict] = field(default_factory=list)
    attempts: int = 0
    estimated_cost_usd: float = 0.0

    def event(self, name: str, **data) -> None:
        self.events.append(
            {
                "name": name,
                "data": data,
                "elapsed_ms": round((perf_counter() - self.started) * 1000, 2),
            }
        )

    def finish(self):
        self.estimated_cost_usd = round(0.0001 * max(self.attempts, 1), 6)
        self.event("complete", attempts=self.attempts, cost_usd=self.estimated_cost_usd)
        return self
