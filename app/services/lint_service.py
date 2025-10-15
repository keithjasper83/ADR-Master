"""Service for ADR linting and validation."""

from typing import List, Dict, Any
from app.models.adr import ADR
import re


class LintIssue:
    """Represents a linting issue."""
    
    def __init__(self, severity: str, message: str, field: str = None):
        self.severity = severity  # 'error', 'warning', 'info'
        self.message = message
        self.field = field
    
    def to_dict(self):
        return {
            "severity": self.severity,
            "message": self.message,
            "field": self.field
        }


class LintService:
    """Service for linting ADRs."""
    
    @staticmethod
    def lint_adr(adr: ADR) -> List[LintIssue]:
        """Lint an ADR for common issues."""
        issues = []
        
        # Check title
        if not adr.title or len(adr.title) < 10:
            issues.append(LintIssue(
                "error",
                "Title must be at least 10 characters long",
                "title"
            ))
        
        if adr.title and len(adr.title) > 100:
            issues.append(LintIssue(
                "warning",
                "Title should be concise (under 100 characters)",
                "title"
            ))
        
        # Check context
        if not adr.context or len(adr.context.strip()) < 50:
            issues.append(LintIssue(
                "error",
                "Context section must be at least 50 characters and explain the problem",
                "context"
            ))
        
        # Check decision
        if not adr.decision or len(adr.decision.strip()) < 50:
            issues.append(LintIssue(
                "error",
                "Decision section must be at least 50 characters and clearly state the decision",
                "decision"
            ))
        
        # Check consequences
        if not adr.consequences or len(adr.consequences.strip()) < 30:
            issues.append(LintIssue(
                "warning",
                "Consequences section should describe the impact of the decision",
                "consequences"
            ))
        
        # Check for passive voice (simple check)
        if adr.decision and LintService._has_excessive_passive_voice(adr.decision):
            issues.append(LintIssue(
                "info",
                "Consider using more active voice in the decision section",
                "decision"
            ))
        
        # Check for vague language
        vague_words = ['maybe', 'probably', 'possibly', 'might', 'could', 'should']
        decision_lower = (adr.decision or "").lower()
        for word in vague_words:
            if word in decision_lower:
                issues.append(LintIssue(
                    "warning",
                    f"Avoid vague language like '{word}' - be decisive",
                    "decision"
                ))
                break
        
        return issues
    
    @staticmethod
    def _has_excessive_passive_voice(text: str) -> bool:
        """Simple check for passive voice indicators."""
        passive_indicators = ['was', 'were', 'been', 'being', 'is', 'are']
        words = text.lower().split()
        passive_count = sum(1 for word in words if word in passive_indicators)
        return passive_count > len(words) * 0.15  # More than 15% passive indicators
    
    @staticmethod
    def lint_markdown(content: str) -> List[LintIssue]:
        """Lint markdown formatting."""
        issues = []
        lines = content.split('\n')
        
        # Check for proper heading hierarchy
        heading_levels = []
        for i, line in enumerate(lines, 1):
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                heading_levels.append(level)
        
        # Check for skipped heading levels
        for i in range(1, len(heading_levels)):
            if heading_levels[i] - heading_levels[i-1] > 1:
                issues.append(LintIssue(
                    "warning",
                    "Heading levels should not skip (e.g., # to ###)",
                    "formatting"
                ))
                break
        
        # Check for trailing whitespace
        for i, line in enumerate(lines, 1):
            if line.endswith(' ') or line.endswith('\t'):
                issues.append(LintIssue(
                    "info",
                    f"Line {i} has trailing whitespace",
                    "formatting"
                ))
        
        return issues
    
    @staticmethod
    def get_lint_summary(issues: List[LintIssue]) -> Dict[str, Any]:
        """Get summary of lint issues."""
        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]
        info = [i for i in issues if i.severity == "info"]
        
        return {
            "total": len(issues),
            "errors": len(errors),
            "warnings": len(warnings),
            "info": len(info),
            "issues": [i.to_dict() for i in issues]
        }
