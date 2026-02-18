"""
API documentation generator for Agentfier.

Produces Markdown-formatted API documentation from the ``api_architecture``
and ``auth`` dimensions of an ``AnalysisResult``.
"""

import logging

from agentfier.models.analysis import AnalysisResult

logger = logging.getLogger(__name__)


class ApiDocGenerator:
    """Generates API documentation in Markdown format."""

    def generate(self, analysis: AnalysisResult) -> str | None:
        """Generate API documentation in markdown format from analysis results.

        Returns ``None`` when the analysis contains no API architecture data.
        """
        if not analysis.api_architecture:
            return None

        api = analysis.api_architecture
        lines = [
            "# API Documentation",
            "",
            f"**API Style:** {api.api_style}",
            f"**Total Endpoints:** {api.total_endpoints}",
            f"**Versioning Strategy:** {api.versioning_strategy}",
            f"**Documentation Format:** {api.documentation_format}",
            f"**Rate Limiting:** {'Yes' if api.rate_limiting else 'No'}",
            "",
            "## Endpoints",
            "",
            "| Method | Path | Description |",
            "|--------|------|-------------|",
        ]

        for ep in api.endpoints:
            method = (
                ep.get("method", "GET")
                if isinstance(ep, dict)
                else getattr(ep, "method", "GET")
            )
            path = (
                ep.get("path", "")
                if isinstance(ep, dict)
                else getattr(ep, "path", "")
            )
            desc = (
                ep.get("description", "")
                if isinstance(ep, dict)
                else getattr(ep, "description", "")
            )
            lines.append(f"| {method} | {path} | {desc} |")

        # Add auth info if available
        if analysis.auth:
            lines.extend(
                [
                    "",
                    "## Authentication",
                    "",
                    f"**Methods:** {', '.join(analysis.auth.methods)}",
                    f"**Authorization Pattern:** {analysis.auth.authorization_pattern}",
                ]
            )
            if analysis.auth.identity_providers:
                lines.append(
                    f"**Identity Providers:** {', '.join(analysis.auth.identity_providers)}"
                )

        return "\n".join(lines)
