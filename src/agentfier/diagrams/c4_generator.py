"""
C4 diagram generator for Agentfier.

Generates C4-model diagrams (Context, Container, Component) by asking
Claude for Graphviz DOT source and rendering it to SVG/PNG.
"""

import json
import logging
from pathlib import Path

from agentfier.claude.client import ClaudeClient
from agentfier.models.analysis import AnalysisResult

logger = logging.getLogger(__name__)


class C4DiagramGenerator:
    """Produces C4 diagrams at three levels from an ``AnalysisResult``."""

    def __init__(
        self,
        claude_client: ClaudeClient,
        output_dir: str = "data/outputs",
    ):
        self.claude = claude_client
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(self, analysis: AnalysisResult) -> dict[str, Path]:
        """Generate all three C4 diagram levels.

        Returns a mapping of level name to the primary output file path.
        """
        results: dict[str, Path] = {}
        context = self._build_analysis_context(analysis)

        for level in ["context", "container", "component"]:
            try:
                path = self._generate_level(context, level)
                if path:
                    results[level] = path
            except Exception as e:
                logger.error(f"Failed to generate C4 {level} diagram: {e}")

        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_analysis_context(self, analysis: AnalysisResult) -> str:
        """Build a text summary of the analysis for Claude to use in
        diagram generation."""
        parts = [f"System: {analysis.input_source}"]

        if analysis.tech_stack:
            parts.append(
                f"Tech Stack: {json.dumps(analysis.tech_stack.model_dump(), default=str)}"
            )
        if analysis.integrations:
            parts.append(
                f"Integrations: {json.dumps(analysis.integrations.model_dump(), default=str)}"
            )
        if analysis.data_layer:
            parts.append(
                f"Data Layer: {json.dumps(analysis.data_layer.model_dump(), default=str)}"
            )
        if analysis.api_architecture:
            parts.append(
                f"API Architecture: {json.dumps(analysis.api_architecture.model_dump(), default=str)}"
            )
        if analysis.auth:
            parts.append(
                f"Auth: {json.dumps(analysis.auth.model_dump(), default=str)}"
            )
        if analysis.infrastructure:
            parts.append(
                f"Infrastructure: {json.dumps(analysis.infrastructure.model_dump(), default=str)}"
            )
        if analysis.frontend:
            parts.append(
                f"Frontend: {json.dumps(analysis.frontend.model_dump(), default=str)}"
            )

        return "\n\n".join(parts)

    def _generate_level(self, context: str, level: str) -> Path | None:
        """Generate a single C4 diagram level."""
        diagram_type = f"c4_{level}"

        try:
            dot_code = self.claude.generate_diagram_spec(context, diagram_type)
        except Exception as e:
            logger.error(f"Claude failed to generate {diagram_type} DOT code: {e}")
            return None

        return self._render_dot(dot_code, f"c4_{level}")

    def _render_dot(self, dot_code: str, name: str) -> Path | None:
        """Render DOT code to SVG and PNG using graphviz.

        Falls back to saving the raw ``.dot`` file when the ``graphviz``
        package is unavailable or rendering fails.
        """
        try:
            import graphviz

            source = graphviz.Source(dot_code)
            output_path = self.output_dir / name
            # Render SVG
            source.render(str(output_path), format="svg", cleanup=True)
            # Also render PNG
            source.render(str(output_path), format="png", cleanup=True)
            logger.info(
                f"Rendered {name} diagram to {output_path}.svg and {output_path}.png"
            )
            return Path(f"{output_path}.svg")
        except ImportError:
            logger.error(
                "graphviz Python package not installed. pip install graphviz"
            )
            # Save DOT source as fallback
            dot_path = self.output_dir / f"{name}.dot"
            dot_path.write_text(dot_code)
            return dot_path
        except Exception as e:
            logger.error(f"Failed to render {name}: {e}")
            # Save DOT source as fallback
            dot_path = self.output_dir / f"{name}.dot"
            dot_path.write_text(dot_code)
            return dot_path
