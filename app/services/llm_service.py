"""Service for LLM integration."""

from typing import Optional, Dict, Any
from app.config import settings
import asyncio


class LLMService:
    """Service for LLM operations."""
    
    @staticmethod
    async def compile_adr(
        context: str,
        requirements: str,
        provider: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Compile an ADR using LLM."""
        provider = provider or settings.default_llm_provider
        model = model or settings.default_llm_model
        
        prompt = f"""Generate an Architecture Decision Record (ADR) in MADR format based on:

Context:
{context}

Requirements:
{requirements}

Please provide:
1. A clear title
2. Context and problem statement
3. Decision made
4. Consequences (positive and negative)
5. Options considered
6. Pros and cons of each option

Format the response as a structured ADR."""
        
        try:
            if provider == "openai" and settings.openai_api_key:
                return await LLMService._call_openai(prompt, model)
            elif provider == "anthropic" and settings.anthropic_api_key:
                return await LLMService._call_anthropic(prompt, model)
            else:
                return {
                    "success": False,
                    "error": f"Provider '{provider}' not configured or API key missing"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def _call_openai(prompt: str, model: str) -> Dict[str, Any]:
        """Call OpenAI API."""
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert in writing Architecture Decision Records."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "provider": "openai",
                "model": model
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"OpenAI API error: {str(e)}"
            }
    
    @staticmethod
    async def _call_anthropic(prompt: str, model: str) -> Dict[str, Any]:
        """Call Anthropic API."""
        try:
            from anthropic import AsyncAnthropic
            
            client = AsyncAnthropic(api_key=settings.anthropic_api_key)
            response = await client.messages.create(
                model=model,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "success": True,
                "content": response.content[0].text,
                "provider": "anthropic",
                "model": model
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Anthropic API error: {str(e)}"
            }
    
    @staticmethod
    async def refine_adr(adr_content: str, feedback: str) -> Dict[str, Any]:
        """Refine an ADR based on feedback."""
        prompt = f"""Refine this Architecture Decision Record based on the feedback:

ADR Content:
{adr_content}

Feedback:
{feedback}

Please provide an improved version addressing the feedback."""
        
        provider = settings.default_llm_provider
        model = settings.default_llm_model
        
        if provider == "openai" and settings.openai_api_key:
            return await LLMService._call_openai(prompt, model)
        elif provider == "anthropic" and settings.anthropic_api_key:
            return await LLMService._call_anthropic(prompt, model)
        else:
            return {
                "success": False,
                "error": "No LLM provider configured"
            }
