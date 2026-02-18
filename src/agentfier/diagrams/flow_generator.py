"""
Flow diagram generator for Agentfier.

Generates user-flow diagrams by asking Claude for Graphviz DOT source
and rendering it to SVG/PNG.
"""

import json
import logging
from pathlib import Path

from agentfier.claude.client import ClaudeClient
from agentfier.models.analysis import AnalysisResult

logger = logging.getLogger(__name__)


class FlowDiagramGenerator:
    """Produces a user-flow diagram from an ``AnalysisResult``."""

    def __init__(
        self,
        claude_client: ClaudeClient,
        output_dir: str = "data/outputs",
    ):
        self.claude = claude_client
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, analysis: AnalysisResult) -> Path | None:
        """Generate a user flow diagram from the analysis results."""
        context_parts: list[str] = []

        if analysis.api_architecture:
            context_parts.append(
                f"API Endpoints: {json.dumps(analysis.api_architecture.model_dump(), default=str)}"
            )
        if analysis.business_logic:
            context_parts.append(
                f"Business Logic: {json.dumps(analysis.business_logic.model_dump(), default=str)}"
            )
        if analysis.auth:
            context_parts.append(
                f"Auth Flow: {json.dumps(analysis.auth.model_dump(), default=str)}"
            )
        if analysis.frontend:
            context_parts.append(
                f"Frontend: {json.dumps(analysis.frontend.model_dump(), default=str)}"
            )

        if not context_parts:
            logger.warning(
                "No relevant analysis results for flow diagram generation."
            )
            return None

        context = "\n\n".join(context_parts)

        try:
            dot_code = self.claude.generate_flow_diagram(context)
            return self._render_dot(dot_code, "user_flow")
        except Exception as e:
            logger.error(f"Failed to generate flow diagram: {e}")
            return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _render_dot(self, dot_code: str, name: str) -> Path | None:
        """Render DOT code to SVG using graphviz.

        Falls back to saving the raw ``.dot`` file when the ``graphviz``
        package is unavailable or rendering fails.
        """
        try:
            import graphviz

            source = graphviz.Source(dot_code)
            output_path = self.output_dir / name
            source.render(str(output_path), format="svg", cleanup=True)
            source.render(str(output_path), format="png", cleanup=True)
            return Path(f"{output_path}.svg")
        except Exception as e:
            logger.error(f"Failed to render {name}: {e}")
            dot_path = self.output_dir / f"{name}.dot"
            dot_path.write_text(dot_code)
            return dot_path
