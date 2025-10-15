"""Invoke tasks for ADR-Master."""
from invoke import task


@task
def install(c):
    """Install production dependencies."""
    c.run("pip install -e .")


@task
def dev(c):
    """Install development dependencies."""
    c.run("pip install -e '.[dev]'")


@task
def lint(c):
    """Run ruff linter."""
    c.run("ruff check app tests")


@task
def format(c):
    """Format code with black and ruff."""
    c.run("black app tests")
    c.run("ruff check --fix app tests")


@task
def typecheck(c):
    """Run mypy type checker."""
    c.run("mypy app")


@task
def security(c):
    """Run bandit security scanner."""
    c.run("bandit -r app -ll")


@task
def test(c, cov=True):
    """Run pytest."""
    if cov:
        c.run("pytest --cov=app --cov-report=term-missing --cov-report=html")
    else:
        c.run("pytest -v")


@task
def clean(c):
    """Remove build artifacts and caches."""
    c.run("rm -rf build dist *.egg-info")
    c.run("rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov")
    c.run("find . -type d -name __pycache__ -exec rm -rf {} + || true")
    c.run("find . -type f -name '*.pyc' -delete")


@task
def run(c):
    """Run the application locally."""
    c.run("uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")


@task
def docker_build(c):
    """Build Docker image."""
    c.run("docker build -t adr-master .")


@task
def docker_run(c):
    """Run Docker container."""
    c.run("docker run -p 8000:8000 -v $(pwd)/ADR:/app/ADR adr-master")
