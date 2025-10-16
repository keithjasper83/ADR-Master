# Contributing to ADR-Master

Thank you for your interest in contributing to ADR-Master! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report:
- Check existing issues to avoid duplicates
- Test with the latest version
- Collect relevant information (OS, Python version, error messages)

Create a bug report with:
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Error messages and logs

### Suggesting Enhancements

Enhancement suggestions are welcome! Include:
- Clear use case
- Expected behavior
- Examples if applicable
- Why this would be useful

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write/update tests
5. Run linting and tests
6. Commit with clear messages
7. Push to your fork
8. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.12+
- Git
- (Optional) Docker

### Setup Steps

```bash
# Clone repository
git clone https://github.com/keithjasper83/ADR-Master.git
cd ADR-Master

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Start application
make run
```

### Using Docker

```bash
# Build
docker build -t adr-master-dev .

# Run
docker-compose up
```

### Using Devcontainer

Open in VS Code with Remote-Containers extension and reopen in container.

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

Follow the project structure:
```
app/
  api/          # API endpoints
  core/         # Core business logic
  db/           # Database setup
  models/       # SQLAlchemy models
  schemas/      # Pydantic schemas
  services/     # Business services
  templates/    # HTML templates
```

### 3. Write Tests

- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- Maintain >90% coverage

Example test:
```python
def test_create_draft(client):
    response = client.post(
        "/api/adr/draft",
        json={"title": "Test", "problem": "Test", "context": "Test"}
    )
    assert response.status_code == 200
    assert "draft_path" in response.json()
```

### 4. Run Quality Checks

```bash
# Format code
make format

# Lint
make lint

# Type check
make type-check

# Security scan
make security

# Run tests
make test
```

Or use Nox:
```bash
nox
```

### 5. Commit Changes

Write clear, descriptive commit messages:

```
feat: add support for custom ADR templates

- Add template management API
- Update UI to allow template selection
- Add tests for template functionality

Closes #123
```

Commit types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Build/tool changes

### 6. Push and Create PR

```bash
git push origin feature/my-feature
```

Create Pull Request with:
- Clear title and description
- Link to related issues
- Screenshots if UI changes
- Test results

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Max line length: 100 characters
- Use Black for formatting
- Use Ruff for linting

Example:
```python
from typing import Optional

def create_draft(
    title: str,
    problem: str,
    context: str,
    options: Optional[str] = None,
) -> tuple[str, str]:
    """Create a new ADR draft.
    
    Args:
        title: ADR title
        problem: Problem statement
        context: Context and background
        options: Optional considered options
    
    Returns:
        Tuple of (draft_path, slug)
    """
    # Implementation
    pass
```

### Documentation

- Add docstrings to all public functions/classes
- Update README if adding features
- Add examples for new functionality
- Update API docs for new endpoints

### Tests

- Test happy paths and edge cases
- Use descriptive test names
- Mock external dependencies
- Aim for >90% coverage

## Project Structure

```
ADR-Master/
├── app/                    # Main application
│   ├── api/               # API endpoints (FastAPI)
│   ├── core/              # Core business logic
│   ├── db/                # Database (SQLAlchemy)
│   ├── models/            # Data models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business services
│   ├── templates/         # Jinja2 templates
│   └── static/            # Static assets
├── mcp_tools/             # MCP tools adapter
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── examples/              # Examples and templates
├── docs/                  # Documentation
├── ADR/                   # Final ADRs
│   └── Draft/            # Draft ADRs
└── _logs/                # Application logs
```

## Adding New Features

### New API Endpoint

1. Define schema in `app/schemas/`
2. Implement service in `app/services/`
3. Create endpoint in `app/api/`
4. Add tests in `tests/`
5. Update API documentation

### New Service

1. Create service file in `app/services/`
2. Define interface/methods
3. Add database models if needed
4. Write unit tests
5. Update dependencies

### New Integration Hook

1. Update `Integration` model if needed
2. Add hook execution in relevant service
3. Document hook in README
4. Add example usage

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Tests

```bash
# Unit tests only
pytest tests/unit/

# Specific file
pytest tests/unit/test_adr_service.py

# Specific test
pytest tests/unit/test_adr_service.py::test_create_draft
```

### With Coverage

```bash
pytest --cov=app --cov-report=html
# Open htmlcov/index.html
```

### Test Fixtures

Use fixtures from `tests/conftest.py`:

```python
def test_something(client, test_db, test_settings):
    # client: TestClient
    # test_db: SQLAlchemy session
    # test_settings: Test settings
    pass
```

## Documentation

### API Documentation

Update `docs/API.md` for new endpoints:

```markdown
### POST /api/new-endpoint

Description of endpoint.

**Request:**
...

**Response:**
...
```

### Code Documentation

Add docstrings:

```python
def function(param: str) -> int:
    """Short description.
    
    Longer description if needed.
    
    Args:
        param: Parameter description
    
    Returns:
        Return value description
    
    Raises:
        ValueError: When something is wrong
    """
    pass
```

## Review Process

1. Automated checks run on PR
2. Maintainer reviews code
3. Discussion and revisions
4. Approval and merge

### Review Criteria

- Code quality and style
- Test coverage
- Documentation
- Performance impact
- Breaking changes

## Getting Help

- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: Questions and ideas
- Documentation: Check `docs/` directory

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors are recognized in:
- GitHub contributors page
- Release notes
- Documentation credits

Thank you for contributing to ADR-Master!
