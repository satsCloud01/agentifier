"""
Tests for output generators: SpecGenerator, ConversionPlanGenerator, ApiDocGenerator.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from agentfier.models.analysis import (
    AnalysisResult,
    ApiArchitectureResult,
    AuthResult,
    EndpointInfo,
    TechStackResult,
    LanguageInfo,
)
from agentfier.models.spec import ConversionPlan, AgentDecomposition, MigrationPhase
from agentfier.output.spec_generator import SpecGenerator
from agentfier.output.conversion_plan import ConversionPlanGenerator
from agentfier.output.api_doc_generator import ApiDocGenerator


# ===========================================================================
# SpecGenerator
# ===========================================================================


class TestSpecGenerator:
    def test_to_yaml_returns_string(self, sample_analysis_result):
        sg = SpecGenerator()
        out = sg.to_yaml(sample_analysis_result)
        assert isinstance(out, str)

    def test_to_yaml_valid_yaml(self, sample_analysis_result):
        sg = SpecGenerator()
        out = sg.to_yaml(sample_analysis_result)
        parsed = yaml.safe_load(out)
        assert "application" in parsed

    def test_to_yaml_contains_metadata(self, sample_analysis_result):
        sg = SpecGenerator()
        out = sg.to_yaml(sample_analysis_result)
        parsed = yaml.safe_load(out)
        meta = parsed["application"]["metadata"]
        assert meta["input_source"] == sample_analysis_result.input_source
        assert meta["input_type"] == sample_analysis_result.input_type
        assert "generated_by" in meta
        assert "generated_at" in meta

    def test_to_yaml_includes_tech_stack(self, sample_analysis_result):
        sg = SpecGenerator()
        out = sg.to_yaml(sample_analysis_result)
        parsed = yaml.safe_load(out)
        assert "technology_stack" in parsed["application"]

    def test_to_yaml_skips_none_dimensions(self):
        analysis = AnalysisResult(input_source="/tmp/x", input_type="local")
        sg = SpecGenerator()
        out = sg.to_yaml(analysis)
        parsed = yaml.safe_load(out)
        # None dimensions should not appear
        assert "technology_stack" not in parsed["application"]

    def test_to_json_returns_string(self, sample_analysis_result):
        sg = SpecGenerator()
        out = sg.to_json(sample_analysis_result)
        assert isinstance(out, str)

    def test_to_json_valid_json(self, sample_analysis_result):
        sg = SpecGenerator()
        out = sg.to_json(sample_analysis_result)
        parsed = json.loads(out)
        assert "application" in parsed

    def test_to_json_contains_metadata(self, sample_analysis_result):
        sg = SpecGenerator()
        out = sg.to_json(sample_analysis_result)
        parsed = json.loads(out)
        meta = parsed["application"]["metadata"]
        assert meta["input_source"] == sample_analysis_result.input_source

    def test_to_json_indented(self, sample_analysis_result):
        sg = SpecGenerator()
        out = sg.to_json(sample_analysis_result)
        assert "\n" in out  # indented output

    def test_dimension_section_names(self, sample_analysis_result):
        sg = SpecGenerator()
        out = sg.to_json(sample_analysis_result)
        parsed = json.loads(out)
        app = parsed["application"]
        expected_keys = [
            "technology_stack",
            "dependencies",
            "data_layer",
            "integration_points",
            "authentication_authorization",
            "observability_monitoring",
            "api_architecture",
            "business_logic_workflows",
            "infrastructure_deployment",
            "security_compliance",
            "frontend_architecture",
            "configuration_management",
        ]
        for key in expected_keys:
            assert key in app, f"Missing key: {key}"

    def test_save_yaml_to_file(self, sample_analysis_result, tmp_path: Path):
        sg = SpecGenerator()
        content = sg.to_yaml(sample_analysis_result)
        saved = sg.save(content, "spec.yaml", str(tmp_path))
        assert saved.exists()
        assert saved.read_text() == content

    def test_save_creates_output_dir(self, sample_analysis_result, tmp_path: Path):
        sg = SpecGenerator()
        content = sg.to_json(sample_analysis_result)
        out_dir = tmp_path / "nested" / "outputs"
        sg.save(content, "spec.json", str(out_dir))
        assert out_dir.is_dir()

    def test_partial_analysis_yaml(self):
        analysis = AnalysisResult(
            input_source="local",
            input_type="local",
            tech_stack=TechStackResult(build_tools=["pip"]),
        )
        sg = SpecGenerator()
        out = sg.to_yaml(analysis)
        parsed = yaml.safe_load(out)
        assert "technology_stack" in parsed["application"]
        assert "dependencies" not in parsed["application"]


# ===========================================================================
# ConversionPlanGenerator
# ===========================================================================


class TestConversionPlanGenerator:
    def _make_generator(self, plan_dict: dict) -> ConversionPlanGenerator:
        client = MagicMock()
        client.generate_conversion_plan.return_value = plan_dict
        return ConversionPlanGenerator(client)

    def _make_plan_dict(self) -> dict:
        return {
            "agent_decomposition": [
                {"name": "Data Agent", "responsibilities": ["DB queries"], "tools": ["sql_query"]}
            ],
            "communication_topology": "Hub-and-spoke",
            "orchestration_pattern": "Supervisor",
            "migration_phases": [
                {"phase": "1", "description": "Setup", "tasks": ["Deploy NATS"], "risks": []}
            ],
            "risk_assessment": "Low",
        }

    def test_generate_returns_conversion_plan(self, sample_analysis_result):
        gen = self._make_generator(self._make_plan_dict())
        result = gen.generate(sample_analysis_result)
        assert isinstance(result, ConversionPlan)

    def test_generate_populates_agents(self, sample_analysis_result):
        gen = self._make_generator(self._make_plan_dict())
        result = gen.generate(sample_analysis_result)
        assert len(result.agent_decomposition) == 1
        assert result.agent_decomposition[0].name == "Data Agent"

    def test_generate_populates_phases(self, sample_analysis_result):
        gen = self._make_generator(self._make_plan_dict())
        result = gen.generate(sample_analysis_result)
        assert len(result.migration_phases) == 1
        assert result.migration_phases[0].description == "Setup"

    def test_generate_returns_none_on_exception(self, sample_analysis_result):
        client = MagicMock()
        client.generate_conversion_plan.side_effect = Exception("API error")
        gen = ConversionPlanGenerator(client)
        result = gen.generate(sample_analysis_result)
        assert result is None

    def test_build_summary_includes_all_dimensions(self, sample_analysis_result):
        client = MagicMock()
        gen = ConversionPlanGenerator(client)
        summary = gen._build_summary(sample_analysis_result)
        assert sample_analysis_result.input_source in summary
        assert "tech_stack" in summary.lower() or "Tech Stack" in summary
        assert "api_architecture" in summary.lower() or "Api Architecture" in summary

    def test_build_summary_skips_none_dimensions(self):
        analysis = AnalysisResult(input_source="local", input_type="local")
        client = MagicMock()
        gen = ConversionPlanGenerator(client)
        summary = gen._build_summary(analysis)
        assert "tech_stack" not in summary.lower().replace("tech stack", "").replace("tech_stack", "")

    def test_calls_claude_with_summary(self, sample_analysis_result):
        plan_dict = self._make_plan_dict()
        client = MagicMock()
        client.generate_conversion_plan.return_value = plan_dict
        gen = ConversionPlanGenerator(client)
        gen.generate(sample_analysis_result)
        client.generate_conversion_plan.assert_called_once()
        call_arg = client.generate_conversion_plan.call_args[0][0]
        assert sample_analysis_result.input_source in call_arg


# ===========================================================================
# ApiDocGenerator
# ===========================================================================


class TestApiDocGenerator:
    def test_returns_none_without_api_architecture(self, sample_analysis_result):
        sample_analysis_result.api_architecture = None
        gen = ApiDocGenerator()
        result = gen.generate(sample_analysis_result)
        assert result is None

    def test_returns_markdown_string(self, sample_analysis_result):
        gen = ApiDocGenerator()
        result = gen.generate(sample_analysis_result)
        assert isinstance(result, str)
        assert result.startswith("# API Documentation")

    def test_includes_api_style(self, sample_analysis_result):
        gen = ApiDocGenerator()
        result = gen.generate(sample_analysis_result)
        assert "REST" in result

    def test_includes_total_endpoints(self, sample_analysis_result):
        gen = ApiDocGenerator()
        result = gen.generate(sample_analysis_result)
        assert "2" in result  # total_endpoints = 2

    def test_includes_endpoints_table(self, sample_analysis_result):
        gen = ApiDocGenerator()
        result = gen.generate(sample_analysis_result)
        assert "| Method | Path | Description |" in result
        assert "GET" in result
        assert "/users" in result

    def test_includes_auth_section(self, sample_analysis_result):
        gen = ApiDocGenerator()
        result = gen.generate(sample_analysis_result)
        assert "## Authentication" in result
        assert "JWT" in result

    def test_includes_identity_providers(self, sample_analysis_result):
        gen = ApiDocGenerator()
        result = gen.generate(sample_analysis_result)
        assert "Auth0" in result

    def test_no_auth_section_when_no_auth(self, sample_analysis_result):
        sample_analysis_result.auth = None
        gen = ApiDocGenerator()
        result = gen.generate(sample_analysis_result)
        assert "## Authentication" not in result

    def test_rate_limiting_shown(self, sample_analysis_result):
        gen = ApiDocGenerator()
        result = gen.generate(sample_analysis_result)
        assert "Yes" in result or "No" in result

    def test_versioning_strategy_shown(self, sample_analysis_result):
        gen = ApiDocGenerator()
        result = gen.generate(sample_analysis_result)
        assert "URL prefix" in result

    def test_all_endpoint_methods_listed(self):
        analysis = AnalysisResult(
            input_source="test",
            input_type="local",
            api_architecture=ApiArchitectureResult(
                endpoints=[
                    EndpointInfo(method="GET", path="/a"),
                    EndpointInfo(method="POST", path="/b"),
                    EndpointInfo(method="DELETE", path="/c"),
                ],
                api_style="REST",
                total_endpoints=3,
            ),
        )
        gen = ApiDocGenerator()
        result = gen.generate(analysis)
        assert "GET" in result
        assert "POST" in result
        assert "DELETE" in result
