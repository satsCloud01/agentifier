"""
Specification generator for Agentfier.

Assembles the final YAML/JSON specification from an AnalysisResult,
including metadata and all populated analysis dimensions.
"""

import json

import yaml
from datetime import datetime
from pathlib import Path

from agentfier.models.analysis import AnalysisResult


class SpecGenerator:
    """Serializes an ``AnalysisResult`` to YAML or JSON spec files."""

    def to_yaml(self, analysis: AnalysisResult) -> str:
        """Serialize AnalysisResult to YAML with metadata header."""
        data = self._build_spec(analysis)
        return yaml.dump(
            data,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )

    def to_json(self, analysis: AnalysisResult) -> str:
        """Serialize AnalysisResult to formatted JSON."""
        data = self._build_spec(analysis)
        return json.dumps(data, indent=2, default=str)

    def _build_spec(self, analysis: AnalysisResult) -> dict:
        """Build the specification dictionary."""
        spec = {
            "application": {
                "metadata": {
                    "generated_by": "Agentfier Analyzer v0.1.0",
                    "generated_at": (
                        analysis.analyzed_at.isoformat()
                        if analysis.analyzed_at
                        else datetime.now().isoformat()
                    ),
                    "input_source": analysis.input_source,
                    "input_type": analysis.input_type,
                },
            }
        }

        # Add each dimension that has results
        dimension_map = {
            "tech_stack": "technology_stack",
            "dependencies": "dependencies",
            "data_layer": "data_layer",
            "integrations": "integration_points",
            "auth": "authentication_authorization",
            "observability": "observability_monitoring",
            "api_architecture": "api_architecture",
            "business_logic": "business_logic_workflows",
            "infrastructure": "infrastructure_deployment",
            "security": "security_compliance",
            "frontend": "frontend_architecture",
            "configuration": "configuration_management",
        }

        for attr, section_name in dimension_map.items():
            result = getattr(analysis, attr, None)
            if result is not None:
                spec["application"][section_name] = result.model_dump()

        return spec

    def save(self, content: str, filename: str, output_dir: str) -> Path:
        """Save spec to file and return path."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        file_path = output_path / filename
        file_path.write_text(content)
        return file_path
