"""GitHub integration service."""
import logging
from pathlib import Path
from typing import Optional

import git

from app.config import get_settings

logger = logging.getLogger(__name__)


class GitHubService:
    """Service for GitHub operations."""

    def __init__(self):
        self.settings = get_settings()
        self.repo_path = self.settings.workdir

    def is_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        try:
            git.Repo(self.repo_path)
            return True
        except git.exc.InvalidGitRepositoryError:
            return False

    def create_adr_branch(self, slug: str) -> Optional[str]:
        """Create a new branch for ADR."""
        if not self.is_git_repo():
            logger.warning("Not a git repository")
            return None
        
        try:
            repo = git.Repo(self.repo_path)
            branch_name = f"adr/{slug}"
            
            # Create new branch
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
            
            return branch_name
        except Exception as e:
            logger.error(f"Failed to create branch: {e}")
            return None

    def commit_and_push(self, file_paths: list[str], message: str) -> bool:
        """Commit and push files."""
        if not self.is_git_repo():
            logger.warning("Not a git repository")
            return False
        
        try:
            repo = git.Repo(self.repo_path)
            
            # Add files
            for file_path in file_paths:
                repo.index.add([file_path])
            
            # Commit
            repo.index.commit(message)
            
            # Push (if remote configured and token available)
            if self.settings.github_token:
                origin = repo.remote(name="origin")
                origin.push()
            
            return True
        except Exception as e:
            logger.error(f"Failed to commit/push: {e}")
            return False

    def sync_adr_directories(self, direction: str = "both") -> tuple[list[str], list[str]]:
        """Sync ADR directories with remote."""
        synced_files = []
        conflicts = []
        
        if not self.is_git_repo():
            logger.warning("Not a git repository")
            return synced_files, conflicts
        
        try:
            repo = git.Repo(self.repo_path)
            
            if direction in ["pull", "both"]:
                # Pull changes
                origin = repo.remote(name="origin")
                origin.pull()
                synced_files.append("Pulled latest changes")
            
            if direction in ["push", "both"]:
                # Stage ADR changes
                adr_files = list(Path(self.settings.adr_dir).glob("**/*.md"))
                adr_draft_files = list(Path(self.settings.adr_draft_dir).glob("**/*.md"))
                
                all_adr_files = adr_files + adr_draft_files
                for file_path in all_adr_files:
                    relative_path = file_path.relative_to(self.repo_path)
                    repo.index.add([str(relative_path)])
                    synced_files.append(str(relative_path))
                
                # Commit if there are changes
                if repo.index.diff("HEAD"):
                    repo.index.commit("Sync ADR changes")
                    
                    if self.settings.github_token:
                        origin = repo.remote(name="origin")
                        origin.push()
            
            return synced_files, conflicts
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return synced_files, [str(e)]
