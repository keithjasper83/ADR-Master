"""Service for ADR operations."""

from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.adr import ADR, ADRStatus
from datetime import datetime
import os
import frontmatter
import markdown


class ADRService:
    """Service for managing ADRs."""
    
    @staticmethod
    async def create_adr(
        db: AsyncSession,
        title: str,
        status: ADRStatus = ADRStatus.DRAFT,
        context: str = "",
        decision: str = "",
        consequences: str = ""
    ) -> ADR:
        """Create a new ADR."""
        # Get next ADR number
        result = await db.execute(select(func.max(ADR.number)))
        max_number = result.scalar_one_or_none() or 0
        next_number = max_number + 1
        
        adr = ADR(
            number=next_number,
            title=title,
            status=status,
            context=context,
            decision=decision,
            consequences=consequences
        )
        db.add(adr)
        await db.flush()
        return adr
    
    @staticmethod
    async def get_adr(db: AsyncSession, adr_id: int) -> Optional[ADR]:
        """Get ADR by ID."""
        result = await db.execute(select(ADR).where(ADR.id == adr_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_adr_by_number(db: AsyncSession, number: int) -> Optional[ADR]:
        """Get ADR by number."""
        result = await db.execute(select(ADR).where(ADR.number == number))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_adrs(
        db: AsyncSession,
        status: Optional[ADRStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ADR]:
        """List ADRs with optional filtering."""
        query = select(ADR)
        if status:
            query = query.where(ADR.status == status)
        query = query.order_by(ADR.number.desc()).limit(limit).offset(offset)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_adr(
        db: AsyncSession,
        adr_id: int,
        **kwargs
    ) -> Optional[ADR]:
        """Update ADR fields."""
        adr = await ADRService.get_adr(db, adr_id)
        if not adr:
            return None
        
        for key, value in kwargs.items():
            if hasattr(adr, key) and value is not None:
                setattr(adr, key, value)
        
        adr.updated_at = datetime.utcnow()
        await db.flush()
        return adr
    
    @staticmethod
    async def delete_adr(db: AsyncSession, adr_id: int) -> bool:
        """Delete an ADR."""
        adr = await ADRService.get_adr(db, adr_id)
        if not adr:
            return False
        await db.delete(adr)
        await db.flush()
        return True
    
    @staticmethod
    def format_as_madr(adr: ADR) -> str:
        """Format ADR as MADR markdown."""
        madr = f"""# {adr.number}. {adr.title}

Date: {adr.created_at.strftime('%Y-%m-%d')}

## Status

{adr.status.upper()}

## Context

{adr.context or 'To be documented'}

## Decision

{adr.decision or 'To be documented'}

## Consequences

{adr.consequences or 'To be documented'}
"""
        
        if adr.options_considered:
            madr += f"\n## Options Considered\n\n{adr.options_considered}\n"
        
        if adr.pros_cons:
            madr += f"\n## Pros and Cons\n\n{adr.pros_cons}\n"
        
        if adr.links:
            madr += f"\n## Links\n\n{adr.links}\n"
        
        return madr
    
    @staticmethod
    def parse_madr(content: str) -> dict:
        """Parse MADR markdown content."""
        post = frontmatter.loads(content)
        html = markdown.markdown(post.content)
        
        # Extract sections
        sections = {}
        current_section = None
        current_content = []
        
        for line in post.content.split('\n'):
            if line.startswith('## '):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line[3:].strip().lower().replace(' ', '_')
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return {
            'metadata': post.metadata,
            'sections': sections,
            'html': html
        }
