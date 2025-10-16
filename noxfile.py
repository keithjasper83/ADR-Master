"""Nox sessions for ADR-Master."""
import nox

nox.options.sessions = ["lint", "type_check", "security", "tests"]
nox.options.reuse_existing_virtualenvs = True

PYTHON_VERSIONS = ["3.12"]


@nox.session(python=PYTHON_VERSIONS)
def lint(session: nox.Session) -> None:
    """Run ruff linter."""
    session.install("ruff")
    session.run("ruff", "check", "app", "tests")


@nox.session(python=PYTHON_VERSIONS)
def format_code(session: nox.Session) -> None:
    """Format code with black and ruff."""
    session.install("black", "ruff")
    session.run("black", "app", "tests")
    session.run("ruff", "check", "--fix", "app", "tests")


@nox.session(python=PYTHON_VERSIONS)
def type_check(session: nox.Session) -> None:
    """Run mypy type checker."""
    session.install("mypy", "types-pyyaml", "types-markdown")
    session.install("-e", ".")
    session.run("mypy", "app")


@nox.session(python=PYTHON_VERSIONS)
def security(session: nox.Session) -> None:
    """Run bandit security scanner."""
    session.install("bandit")
    session.run("bandit", "-r", "app", "-ll")


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run pytest with coverage."""
    session.install("-e", ".[dev]")
    session.run(
        "pytest",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-fail-under=90",
    )


@nox.session(python=PYTHON_VERSIONS)
def tests_no_cov(session: nox.Session) -> None:
    """Run pytest without coverage requirements."""
    session.install("-e", ".[dev]")
    session.run("pytest", "-v")
