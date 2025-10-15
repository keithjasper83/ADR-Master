.PHONY: help install dev lint format type-check security test test-cov clean run docker-build docker-run

help:
	@echo "ADR-Master - Makefile targets"
	@echo "  install       - Install production dependencies"
	@echo "  dev           - Install development dependencies"
	@echo "  lint          - Run ruff linter"
	@echo "  format        - Format code with black and ruff"
	@echo "  type-check    - Run mypy type checker"
	@echo "  security      - Run bandit security scanner"
	@echo "  test          - Run pytest"
	@echo "  test-cov      - Run pytest with coverage report"
	@echo "  clean         - Remove build artifacts and caches"
	@echo "  run           - Run the application locally"
	@echo "  docker-build  - Build Docker image"
	@echo "  docker-run    - Run Docker container"

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

lint:
	ruff check app tests

format:
	black app tests
	ruff check --fix app tests

type-check:
	mypy app

security:
	bandit -r app -ll

test:
	pytest

test-cov:
	pytest --cov=app --cov-report=term-missing --cov-report=html

clean:
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker build -t adr-master .

docker-run:
	docker run -p 8000:8000 -v $(PWD)/ADR:/app/ADR adr-master
