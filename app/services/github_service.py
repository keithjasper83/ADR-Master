"""Service for GitHub integration."""

from typing import Optional, Dict, Any
from github import Github, GithubException
from app.config import settings
from app.models.adr import ADR
from app.services.adr_service import ADRService
import base64


class GitHubService:
    """Service for GitHub operations."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub service."""
        self.token = token or settings.github_token
        self.client = Github(self.token) if self.token else None
    
    async def create_pr_for_adr(
        self,
        repo_name: str,
        adr: ADR,
        base_branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a GitHub PR for an ADR."""
        if not self.client:
            return {
                "success": False,
                "error": "GitHub token not configured"
            }
        
        try:
            repo = self.client.get_repo(repo_name)
            base_branch = base_branch or settings.github_default_branch
            
            # Create branch name
            branch_name = f"adr-{adr.number}-{adr.title.lower().replace(' ', '-')[:30]}"
            
            # Get base branch reference
            base_ref = repo.get_git_ref(f"heads/{base_branch}")
            base_sha = base_ref.object.sha
            
            # Create new branch
            try:
                repo.create_git_ref(f"refs/heads/{branch_name}", base_sha)
            except GithubException as e:
                if e.status == 422:  # Branch already exists
                    return {
                        "success": False,
                        "error": f"Branch {branch_name} already exists"
                    }
                raise
            
            # Create/update file
            file_path = f"{settings.adr_directory}/ADR-{adr.number:04d}-{adr.title.replace(' ', '-')}.md"
            content = ADRService.format_as_madr(adr)
            
            try:
                # Try to get existing file
                existing_file = repo.get_contents(file_path, ref=branch_name)
                repo.update_file(
                    path=file_path,
                    message=f"Update ADR-{adr.number}: {adr.title}",
                    content=content,
                    sha=existing_file.sha,
                    branch=branch_name
                )
            except GithubException:
                # File doesn't exist, create it
                repo.create_file(
                    path=file_path,
                    message=f"Add ADR-{adr.number}: {adr.title}",
                    content=content,
                    branch=branch_name
                )
            
            # Create pull request
            pr = repo.create_pull(
                title=f"ADR-{adr.number}: {adr.title}",
                body=f"""## Architecture Decision Record

**Status:** {adr.status.upper()}

**Context:**
{adr.context}

**Decision:**
{adr.decision}

**Consequences:**
{adr.consequences}

This PR adds/updates ADR-{adr.number}.
""",
                head=branch_name,
                base=base_branch
            )
            
            return {
                "success": True,
                "pr_number": pr.number,
                "pr_url": pr.html_url,
                "branch": branch_name
            }
            
        except GithubException as e:
            return {
                "success": False,
                "error": f"GitHub API error: {e.data.get('message', str(e))}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def sync_adrs_from_repo(
        self,
        repo_name: str,
        branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """Sync ADRs from a GitHub repository."""
        if not self.client:
            return {
                "success": False,
                "error": "GitHub token not configured"
            }
        
        try:
            repo = self.client.get_repo(repo_name)
            branch = branch or settings.github_default_branch
            
            # Get ADR directory contents
            try:
                contents = repo.get_contents(settings.adr_directory, ref=branch)
            except GithubException:
                return {
                    "success": False,
                    "error": f"ADR directory not found: {settings.adr_directory}"
                }
            
            synced_files = []
            for content_file in contents:
                if content_file.name.endswith('.md'):
                    file_content = base64.b64decode(content_file.content).decode('utf-8')
                    synced_files.append({
                        "path": content_file.path,
                        "sha": content_file.sha,
                        "content": file_content
                    })
            
            return {
                "success": True,
                "synced_count": len(synced_files),
                "files": synced_files
            }
            
        except GithubException as e:
            return {
                "success": False,
                "error": f"GitHub API error: {e.data.get('message', str(e))}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
