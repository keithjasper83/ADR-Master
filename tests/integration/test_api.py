"""Integration tests for API endpoints."""
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_create_draft(client: TestClient):
    """Test draft creation endpoint."""
    response = client.post(
        "/api/adr/draft",
        json={
            "title": "Test ADR",
            "problem": "This is a test problem that needs solving",
            "context": "This is the context for testing",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "draft_path" in data
    assert "slug" in data
    assert "001-test-adr.md" in data["slug"]


def test_lint_adr(client: TestClient):
    """Test ADR linting endpoint."""
    # First create a draft
    create_response = client.post(
        "/api/adr/draft",
        json={
            "title": "Test ADR for Linting",
            "problem": "Test problem statement here",
            "context": "Test context for linting",
        },
    )
    
    draft_path = create_response.json()["draft_path"]
    
    # Lint it
    lint_response = client.post("/api/adr/lint", json={"file_path": draft_path})
    
    assert lint_response.status_code == 200
    data = lint_response.json()
    assert "valid" in data
    assert "errors" in data
    assert "warnings" in data


def test_mcp_config(client: TestClient):
    """Test MCP config endpoint."""
    response = client.get("/api/mcp/config")
    assert response.status_code == 200
    data = response.json()
    assert "mcp_base_url" in data
    assert "connected" in data


def test_list_integrations(client: TestClient):
    """Test list integrations endpoint."""
    response = client.get("/api/integrations/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_create_integration(client: TestClient):
    """Test create integration endpoint."""
    response = client.post(
        "/api/integrations/",
        json={
            "name": "Test Plugin",
            "description": "Test plugin for integration",
            "hooks": ["on_draft_create"],
            "config": {},
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Plugin"
    assert data["enabled"] is True


def test_index_project(client: TestClient, test_settings):
    """Test project indexing endpoint."""
    response = client.post("/api/projects/index", json={"path": str(test_settings.workdir)})
    
    assert response.status_code == 200
    data = response.json()
    assert "indexed_files" in data
