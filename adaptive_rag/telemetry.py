import logging
from time import perf_counter

logger = logging.getLogger("adaptive_rag")


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


class Timer:
    def __enter__(self):
        self.started = perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.elapsed_ms = (perf_counter() - self.started) * 1000
