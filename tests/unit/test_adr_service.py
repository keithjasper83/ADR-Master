"""Tests for ADR service."""
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from app.schemas.adr import CreateDraftRequest
from app.services.adr_service import ADRService


def test_create_draft(test_db: Session, test_settings):
    """Test draft creation."""
    service = ADRService(test_db)
    
    request = CreateDraftRequest(
        title="Test ADR",
        problem="This is a test problem",
        context="This is test context",
    )
    
    draft_path, slug = service.create_draft(request)
    
    assert Path(draft_path).exists()
    assert "001-test-adr.md" in draft_path
    assert Path(draft_path).read_text()


def test_generate_slug(test_db: Session):
    """Test slug generation."""
    service = ADRService(test_db)
    
    slug = service._generate_slug("Use FastAPI for Backend")
    assert slug == "use-fastapi-for-backend"
    
    slug = service._generate_slug("API Design: REST vs GraphQL")
    assert slug == "api-design-rest-vs-graphql"


def test_lint_valid_adr(test_db: Session, test_settings):
    """Test linting valid ADR."""
    service = ADRService(test_db)
    
    # Create a valid ADR
    request = CreateDraftRequest(
        title="Valid ADR",
        problem="Test problem",
        context="Test context",
    )
    
    draft_path, _ = service.create_draft(request)
    
    # Lint it
    result = service.lint_adr(draft_path)
    
    assert result.valid
    assert len(result.errors) == 0


def test_lint_invalid_filename(test_db: Session, test_settings):
    """Test linting with invalid filename."""
    service = ADRService(test_db)
    
    # Create file with bad name
    bad_path = test_settings.adr_draft_dir / "bad-name.md"
    bad_path.write_text("# Test\n\n## Status\n\nDraft")
    
    result = service.lint_adr(str(bad_path))
    
    assert not result.valid
    assert any("Filename must match format" in e for e in result.errors)


def test_get_next_adr_number(test_db: Session, test_settings):
    """Test ADR number generation."""
    service = ADRService(test_db)
    
    # First ADR should be 1
    assert service._get_next_adr_number() == 1
    
    # Create a draft
    request = CreateDraftRequest(
        title="First ADR",
        problem="Test",
        context="Test",
    )
    service.create_draft(request)
    
    # Next should be 2
    assert service._get_next_adr_number() == 2
