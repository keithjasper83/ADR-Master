"""Example plugin for ADR-Master integration.

This demonstrates how external tools can register with ADR-Master
to enhance ADR generation and agentic workflows.
"""
import httpx


class RiskAnalyzerPlugin:
    """Example plugin that analyzes ADR risks."""

    def __init__(self, adr_master_url: str = "http://localhost:8000"):
        self.api_base = adr_master_url

    async def register(self) -> None:
        """Register plugin with ADR-Master."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base}/api/integrations/",
                json={
                    "name": "Risk Analyzer",
                    "description": "Analyzes ADRs for potential risks and provides recommendations",
                    "hooks": ["on_draft_create", "on_compile_post"],
                    "config": {"risk_threshold": "medium", "auto_analyze": True},
                },
            )
            response.raise_for_status()
            print("Plugin registered successfully")

    def on_draft_create(self, draft_path: str, metadata: dict) -> dict:
        """Hook called when a new draft is created.

        Args:
            draft_path: Path to the created draft
            metadata: Draft metadata

        Returns:
            dict with analysis results
        """
        # Read draft content
        with open(draft_path) as f:
            content = f.read()

        # Perform risk analysis (simplified example)
        risks = []

        if "security" in content.lower():
            risks.append(
                {"level": "high", "type": "security", "message": "Security implications mentioned"}
            )

        if "database" in content.lower() and "migration" not in content.lower():
            risks.append(
                {
                    "level": "medium",
                    "type": "data",
                    "message": "Database changes without migration plan",
                }
            )

        if "performance" not in content.lower():
            risks.append(
                {
                    "level": "low",
                    "type": "performance",
                    "message": "No performance considerations documented",
                }
            )

        return {
            "analyzed": True,
            "risk_count": len(risks),
            "risks": risks,
            "recommendations": self._generate_recommendations(risks),
        }

    def on_compile_post(self, draft_path: str, compilation_result: dict) -> dict:
        """Hook called after LLM compilation.

        Args:
            draft_path: Path to compiled draft
            compilation_result: Compilation job result

        Returns:
            dict with post-compilation analysis
        """
        return {
            "validated": True,
            "message": "Post-compilation validation complete",
            "suggestions": ["Consider adding more detail to consequences section"],
        }

    def _generate_recommendations(self, risks: list[dict]) -> list[str]:
        """Generate recommendations based on identified risks."""
        recommendations = []

        for risk in risks:
            if risk["type"] == "security":
                recommendations.append(
                    "Add security review section and consider threat modeling"
                )
            elif risk["type"] == "data":
                recommendations.append(
                    "Document data migration strategy and rollback plan"
                )
            elif risk["type"] == "performance":
                recommendations.append(
                    "Add performance impact assessment and monitoring plan"
                )

        return recommendations


# Usage example
async def main():
    """Example usage."""
    plugin = RiskAnalyzerPlugin()

    # Register with ADR-Master
    await plugin.register()

    # Hooks would be called automatically by ADR-Master when events occur
    # This is just an example of calling the hook manually
    result = plugin.on_draft_create(
        "/app/ADR/Draft/001-example.md", {"title": "Example ADR", "status": "Draft"}
    )

    print("Risk Analysis Result:")
    print(f"- Risks found: {result['risk_count']}")
    for risk in result["risks"]:
        print(f"  - [{risk['level']}] {risk['message']}")
    print("\nRecommendations:")
    for rec in result["recommendations"]:
        print(f"  - {rec}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
