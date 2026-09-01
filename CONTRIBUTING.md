# Contributing

1. Create a focused branch.
2. Keep provider integrations optional and injectable.
3. Add regression tests for behavior changes.
4. Run `ruff check adaptive_rag tests benchmarks`.
5. Run `pytest -q` and `python -m benchmarks.run`.
6. Update documentation when architecture or configuration changes.
7. Never commit credentials, generated databases or private datasets.

The project favors small, composable modules over framework-specific coupling.
