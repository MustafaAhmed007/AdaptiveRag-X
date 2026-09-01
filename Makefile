.PHONY: install lint test benchmark run docker

install:
	python -m pip install -e ".[dev]"

lint:
	ruff check adaptive_rag tests benchmarks

test:
	pytest -q

benchmark:
	python -m benchmarks.run

run:
	uvicorn adaptive_rag.api:app --reload

docker:
	docker compose up --build
