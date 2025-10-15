"""ADR service for managing ADR documents."""
import hashlib
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.base import ADRMetadata, ActionLog, CompilationJob
from app.schemas.adr import CreateDraftRequest, LintResult


class ADRService:
    """Service for ADR operations."""

    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def create_draft(self, request: CreateDraftRequest) -> tuple[str, str]:
        """Create a new ADR draft."""
        # Generate slug from title
        slug = self._generate_slug(request.title)
        
        # Get next ADR number
        number = self._get_next_adr_number()
        filename = f"{number:03d}-{slug}.md"
        
        # Create draft file path
        draft_path = self.settings.adr_draft_dir / filename
        
        # Generate MADR content
        content = self._generate_madr_content(
            number=number,
            title=request.title,
            problem=request.problem,
            context=request.context,
            options=request.options,
            decision_hint=request.decision_hint,
            references=request.references,
        )
        
        # Write file
        draft_path.write_text(content)
        
        # Calculate SHA256
        sha256 = self._calculate_sha256(draft_path)
        
        # Save metadata
        metadata = ADRMetadata(
            file_path=str(draft_path),
            title=request.title,
            slug=filename,
            status="Draft",
            sha256=sha256,
        )
        self.db.add(metadata)
        
        # Log action
        log = ActionLog(
            job_id=str(uuid.uuid4()),
            action="create_draft",
            details={"title": request.title, "path": str(draft_path)},
            sha256=sha256,
        )
        self.db.add(log)
        self.db.commit()
        
        return str(draft_path), filename

    def lint_adr(self, file_path: str) -> LintResult:
        """Lint an ADR file."""
        errors = []
        warnings = []
        
        path = Path(file_path)
        if not path.exists():
            errors.append(f"File not found: {file_path}")
            return LintResult(valid=False, errors=errors, warnings=warnings)
        
        content = path.read_text()
        
        # Check filename format
        if not re.match(r"^\d{3}-.+\.md$", path.name):
            errors.append("Filename must match format: NNN-title.md")
        
        # Check required MADR sections
        required_sections = ["Status", "Context", "Decision", "Consequences", "References"]
        for section in required_sections:
            if f"## {section}" not in content:
                errors.append(f"Missing required section: {section}")
        
        # Check status value
        status_match = re.search(r"## Status\s+(\w+)", content)
        if status_match:
            status = status_match.group(1)
            if status not in ["Draft", "Accepted", "Superseded", "Deprecated"]:
                errors.append(f"Invalid status: {status}")
        else:
            errors.append("Could not find status value")
        
        # Check decision summary length (if present)
        decision_match = re.search(r"## Decision\s+(.+?)(?=\n##|\Z)", content, re.DOTALL)
        if decision_match:
            decision = decision_match.group(1).strip()
            first_line = decision.split("\n")[0]
            if len(first_line) > 280:
                warnings.append("Decision summary exceeds 280 characters")
        
        return LintResult(valid=len(errors) == 0, errors=errors, warnings=warnings)

    def promote_adr(self, draft_path: str) -> str:
        """Promote an ADR from draft to final."""
        source = Path(draft_path)
        if not source.exists():
            raise FileNotFoundError(f"Draft not found: {draft_path}")
        
        # Lint first
        lint_result = self.lint_adr(draft_path)
        if not lint_result.valid:
            raise ValueError(f"ADR failed linting: {lint_result.errors}")
        
        # Move to final directory
        target = self.settings.adr_dir / source.name
        
        # Read content and update status
        content = source.read_text()
        content = re.sub(r"## Status\s+Draft", "## Status\n\nAccepted", content)
        
        # Write to final location
        target.write_text(content)
        
        # Update metadata
        metadata = self.db.query(ADRMetadata).filter_by(file_path=str(source)).first()
        if metadata:
            metadata.file_path = str(target)
            metadata.status = "Accepted"
            metadata.sha256 = self._calculate_sha256(target)
        
        # Log action
        log = ActionLog(
            action="promote_adr",
            details={"source": str(source), "target": str(target)},
            sha256=self._calculate_sha256(target),
        )
        self.db.add(log)
        self.db.commit()
        
        # Remove draft
        source.unlink()
        
        return str(target)

    def create_compilation_job(self, draft_path: str, human_notes: Optional[str]) -> str:
        """Create a compilation job."""
        job_id = str(uuid.uuid4())
        
        job = CompilationJob(
            job_id=job_id,
            draft_path=draft_path,
            status="queued",
            logs=[f"Job created at {datetime.utcnow().isoformat()}"],
        )
        self.db.add(job)
        self.db.commit()
        
        return job_id

    def get_job_status(self, job_id: str) -> Optional[CompilationJob]:
        """Get compilation job status."""
        return self.db.query(CompilationJob).filter_by(job_id=job_id).first()

    def _generate_slug(self, title: str) -> str:
        """Generate slug from title."""
        slug = title.lower()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[-\s]+", "-", slug)
        return slug.strip("-")

    def _get_next_adr_number(self) -> int:
        """Get next ADR number."""
        # Check both draft and final directories
        all_files = []
        if self.settings.adr_dir.exists():
            all_files.extend(self.settings.adr_dir.glob("*.md"))
        if self.settings.adr_draft_dir.exists():
            all_files.extend(self.settings.adr_draft_dir.glob("*.md"))
        
        numbers = []
        for file in all_files:
            match = re.match(r"^(\d{3})-", file.name)
            if match:
                numbers.append(int(match.group(1)))
        
        return max(numbers, default=0) + 1

    def _generate_madr_content(
        self,
        number: int,
        title: str,
        problem: str,
        context: str,
        options: Optional[str],
        decision_hint: Optional[str],
        references: Optional[list[str]],
    ) -> str:
        """Generate MADR template content."""
        date = datetime.now().strftime("%Y-%m-%d")
        
        content = f"""# {number}. {title}

Date: {date}

## Status

Draft

## Context

{context}

## Problem Statement

{problem}

## Decision Drivers

* Maintainability
* Performance
* Security
* Developer experience

## Considered Options

"""
        
        if options:
            content += f"{options}\n\n"
        else:
            content += "* Option 1: [To be filled]\n* Option 2: [To be filled]\n\n"
        
        content += "## Decision Outcome\n\n"
        
        if decision_hint:
            content += f"{decision_hint}\n\n"
        else:
            content += "[Decision to be made after analysis]\n\n"
        
        content += """### Consequences

* Good: [To be filled]
* Bad: [To be filled]
* Neutral: [To be filled]

## Pros and Cons of the Options

### Option 1

* Good: [To be filled]
* Bad: [To be filled]

## More Information

"""
        
        if references:
            content += "\n".join(f"* {ref}" for ref in references)
        else:
            content += "[Additional references and context]"
        
        content += "\n\n## References\n\n"
        content += "[Links to related ADRs, documentation, or external resources]\n"
        
        return content

    def _calculate_sha256(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
