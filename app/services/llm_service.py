"""LLM service for ADR compilation."""
import asyncio
import logging
from pathlib import Path
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.base import CompilationJob

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM-based ADR compilation."""

    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    async def compile_adr(self, job_id: str) -> None:
        """Compile ADR using LLM (async background task)."""
        job = self.db.query(CompilationJob).filter_by(job_id=job_id).first()
        if not job:
            logger.error(f"Job not found: {job_id}")
            return
        
        try:
            # Update status
            job.status = "running"
            job.logs.append("Starting compilation...")
            self.db.commit()
            
            # Read draft content
            draft_path = Path(job.draft_path)
            if not draft_path.exists():
                raise FileNotFoundError(f"Draft not found: {job.draft_path}")
            
            content = draft_path.read_text()
            
            job.logs.append("Sending to LLM...")
            self.db.commit()
            
            # Send to LLM
            improved_content = await self._call_llm(content)
            
            if improved_content:
                job.logs.append("LLM processing complete")
                
                # Write improved content
                draft_path.write_text(improved_content)
                
                job.status = "completed"
                job.output_path = str(draft_path)
                job.logs.append("Draft updated successfully")
            else:
                raise ValueError("LLM returned empty response")
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Compilation failed for job {job_id}: {e}")
            job.status = "failed"
            job.error_message = str(e)
            job.logs.append(f"Error: {str(e)}")
            self.db.commit()

    async def _call_llm(self, content: str) -> Optional[str]:
        """Call LLM endpoint with ADR content."""
        prompt = f"""You are an expert in writing Architecture Decision Records (ADRs).
        
Review and improve the following ADR draft. Focus on:
1. Clarity and precision
2. Actionable details
3. Completeness of sections
4. Professional tone
5. Clear decision rationale

Return the improved ADR content maintaining the MADR format.

Draft ADR:
{content}

Improved ADR:"""
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Try Ollama-style endpoint first
                try:
                    response = await client.post(
                        self.settings.llm_endpoint,
                        json={
                            "model": "llama2",
                            "prompt": prompt,
                            "stream": False,
                        },
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        return data.get("response", content)
                except Exception:
                    pass
                
                # Fallback: try OpenAI-compatible endpoint
                try:
                    openai_endpoint = self.settings.llm_endpoint.replace("/generate", "/chat/completions")
                    response = await client.post(
                        openai_endpoint,
                        json={
                            "model": "gpt-3.5-turbo",
                            "messages": [{"role": "user", "content": prompt}],
                        },
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        return data["choices"][0]["message"]["content"]
                except Exception:
                    pass
                
                # If both fail, return original content with a note
                logger.warning("LLM endpoint not available, returning original content")
                return content + "\n\n<!-- LLM enhancement unavailable -->\n"
                
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return None


def start_compilation_background(db: Session, job_id: str) -> None:
    """Start compilation in background (helper for sync contexts)."""
    llm_service = LLMService(db)
    asyncio.create_task(llm_service.compile_adr(job_id))
