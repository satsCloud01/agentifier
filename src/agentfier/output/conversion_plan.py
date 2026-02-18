"""
Conversion plan generator for Agentfier.

Uses Claude to produce a structured ``ConversionPlan`` that describes how
to migrate the analysed application to an agent-native architecture.
"""

import json
import logging

from agentfier.claude.client import ClaudeClient
from agentfier.models.analysis import AnalysisResult
from agentfier.models.spec import ConversionPlan

logger = logging.getLogger(__name__)


class ConversionPlanGenerator:
    """Generates an agent-native conversion plan from an ``AnalysisResult``."""

    def __init__(self, claude_client: ClaudeClient):
        self.claude = claude_client

    def generate(self, analysis: AnalysisResult) -> ConversionPlan | None:
        """Generate an agent-native conversion plan from the full analysis."""
        summary = self._build_summary(analysis)

        try:
            result = self.claude.generate_conversion_plan(summary)
            return ConversionPlan.model_validate(result)
        except Exception as e:
            logger.error(f"Failed to generate conversion plan: {e}")
            return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_summary(self, analysis: AnalysisResult) -> str:
        """Build a comprehensive text summary of all analysis dimensions."""
        parts = [f"Application: {analysis.input_source}"]

        dimension_names = [
            "tech_stack",
            "dependencies",
            "data_layer",
            "integrations",
            "auth",
            "observability",
            "api_architecture",
            "business_logic",
            "infrastructure",
            "security",
            "frontend",
            "configuration",
        ]

        for dim in dimension_names:
            result = getattr(analysis, dim, None)
            if result is not None:
                parts.append(
                    f"\n## {dim.replace('_', ' ').title()}\n"
                    f"{json.dumps(result.model_dump(), indent=2, default=str)}"
                )

        return "\n".join(parts)
