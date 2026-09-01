from dataclasses import dataclass, field
from time import perf_counter
from uuid import uuid4

@dataclass
class Trace:
    trace_id: str = field(default_factory=lambda: uuid4().hex)
    strategy: str = "unknown"
    attempts: int = 0
    events: list[dict] = field(default_factory=list)
    estimated_cost_usd: float = 0.0
    _started: float = field(default_factory=perf_counter, repr=False)

    def event(self, name: str, **data) -> None:
        self.events.append({"name": name, **data})

    @property
    def latency_ms(self) -> float:
        return (perf_counter() - self._started) * 1000
