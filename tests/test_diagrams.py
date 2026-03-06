"""
Tests for C4DiagramGenerator and FlowDiagramGenerator.
All graphviz rendering and Claude calls are mocked.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

from agentfier.diagrams.c4_generator import C4DiagramGenerator
from agentfier.diagrams.flow_generator import FlowDiagramGenerator
from agentfier.models.analysis import (
    AnalysisResult,
    ApiArchitectureResult,
    AuthResult,
    BusinessLogicResult,
    FrontendResult,
    InfrastructureResult,
    IntegrationResult,
    TechStackResult,
)


SAMPLE_DOT = 'digraph { A -> B -> C }'


def _mock_claude(dot_return=SAMPLE_DOT):
    client = MagicMock()
    client.generate_diagram_spec.return_value = dot_return
    client.generate_flow_diagram.return_value = dot_return
    return client


# ===========================================================================
# C4DiagramGenerator
# ===========================================================================


class TestC4DiagramGenerator:
    def test_creates_output_dir(self, tmp_path: Path):
        out_dir = tmp_path / "outputs"
        C4DiagramGenerator(_mock_claude(), output_dir=str(out_dir))
        assert out_dir.is_dir()

    def test_generate_all_produces_three_levels(self, tmp_path: Path, sample_analysis_result):
        client = _mock_claude()
        gen = C4DiagramGenerator(client, output_dir=str(tmp_path))

        with patch("agentfier.diagrams.c4_generator.C4DiagramGenerator._render_dot") as mock_render:
            mock_render.side_effect = lambda dot, name: tmp_path / f"{name}.svg"
            results = gen.generate_all(sample_analysis_result)

        assert "context" in results
        assert "container" in results
        assert "component" in results

    def test_generate_all_calls_claude_three_times(self, tmp_path: Path, sample_analysis_result):
        client = _mock_claude()
        gen = C4DiagramGenerator(client, output_dir=str(tmp_path))

        with patch.object(gen, "_render_dot", return_value=tmp_path / "out.svg"):
            gen.generate_all(sample_analysis_result)

        assert client.generate_diagram_spec.call_count == 3

    def test_generate_all_uses_correct_diagram_types(self, tmp_path: Path, sample_analysis_result):
        client = _mock_claude()
        gen = C4DiagramGenerator(client, output_dir=str(tmp_path))

        with patch.object(gen, "_render_dot", return_value=tmp_path / "out.svg"):
            gen.generate_all(sample_analysis_result)

        calls = [c[0][1] for c in client.generate_diagram_spec.call_args_list]
        assert "c4_context" in calls
        assert "c4_container" in calls
        assert "c4_component" in calls

    def test_generate_all_handles_claude_failure_gracefully(self, tmp_path: Path, sample_analysis_result):
        client = MagicMock()
        client.generate_diagram_spec.side_effect = Exception("API error")
        gen = C4DiagramGenerator(client, output_dir=str(tmp_path))
        results = gen.generate_all(sample_analysis_result)
        # Should not raise; should return empty dict
        assert isinstance(results, dict)

    def test_generate_all_partial_failure(self, tmp_path: Path, sample_analysis_result):
        """Second level fails; other two succeed."""
        client = MagicMock()
        client.generate_diagram_spec.side_effect = [
            SAMPLE_DOT,
            Exception("container fail"),
            SAMPLE_DOT,
        ]
        gen = C4DiagramGenerator(client, output_dir=str(tmp_path))

        with patch.object(gen, "_render_dot", return_value=tmp_path / "out.svg"):
            results = gen.generate_all(sample_analysis_result)

        assert "container" not in results

    def test_build_analysis_context_includes_tech_stack(self, tmp_path: Path, sample_analysis_result):
        gen = C4DiagramGenerator(_mock_claude(), output_dir=str(tmp_path))
        ctx = gen._build_analysis_context(sample_analysis_result)
        assert sample_analysis_result.input_source in ctx
        assert "Tech Stack" in ctx or "tech_stack" in ctx.lower()

    def test_build_analysis_context_includes_integrations(self, tmp_path: Path, sample_analysis_result):
        gen = C4DiagramGenerator(_mock_claude(), output_dir=str(tmp_path))
        ctx = gen._build_analysis_context(sample_analysis_result)
        assert "Integrations" in ctx or "integration" in ctx.lower()

    def test_build_analysis_context_minimal(self, tmp_path: Path):
        gen = C4DiagramGenerator(_mock_claude(), output_dir=str(tmp_path))
        analysis = AnalysisResult(input_source="myapp", input_type="local")
        ctx = gen._build_analysis_context(analysis)
        assert "myapp" in ctx

    def test_render_dot_saves_dot_file_when_graphviz_missing(self, tmp_path: Path):
        gen = C4DiagramGenerator(_mock_claude(), output_dir=str(tmp_path))
        with patch.dict("sys.modules", {"graphviz": None}):
            result = gen._render_dot(SAMPLE_DOT, "c4_context")
        assert result is not None
        # Should be a .dot file
        assert result.suffix == ".dot"
        assert result.read_text() == SAMPLE_DOT

    def test_render_dot_saves_dot_file_on_render_error(self, tmp_path: Path):
        gen = C4DiagramGenerator(_mock_claude(), output_dir=str(tmp_path))

        mock_gv = MagicMock()
        mock_gv.Source.return_value.render.side_effect = Exception("render fail")

        with patch.dict("sys.modules", {"graphviz": mock_gv}):
            result = gen._render_dot(SAMPLE_DOT, "c4_container")

        assert result.suffix == ".dot"

    def test_render_dot_returns_svg_on_success(self, tmp_path: Path):
        gen = C4DiagramGenerator(_mock_claude(), output_dir=str(tmp_path))

        mock_gv = MagicMock()
        with patch.dict("sys.modules", {"graphviz": mock_gv}):
            result = gen._render_dot(SAMPLE_DOT, "c4_component")

        assert result is not None


# ===========================================================================
# FlowDiagramGenerator
# ===========================================================================


class TestFlowDiagramGenerator:
    def test_creates_output_dir(self, tmp_path: Path):
        out_dir = tmp_path / "flow_outputs"
        FlowDiagramGenerator(_mock_claude(), output_dir=str(out_dir))
        assert out_dir.is_dir()

    def test_generate_returns_path(self, tmp_path: Path, sample_analysis_result):
        gen = FlowDiagramGenerator(_mock_claude(), output_dir=str(tmp_path))
        with patch.object(gen, "_render_dot", return_value=tmp_path / "user_flow.svg"):
            result = gen.generate(sample_analysis_result)
        assert result is not None

    def test_generate_calls_claude_generate_flow(self, tmp_path: Path, sample_analysis_result):
        client = _mock_claude()
        gen = FlowDiagramGenerator(client, output_dir=str(tmp_path))
        with patch.object(gen, "_render_dot", return_value=tmp_path / "user_flow.svg"):
            gen.generate(sample_analysis_result)
        client.generate_flow_diagram.assert_called_once()

    def test_generate_returns_none_when_no_context(self, tmp_path: Path):
        analysis = AnalysisResult(input_source="test", input_type="local")
        gen = FlowDiagramGenerator(_mock_claude(), output_dir=str(tmp_path))
        result = gen.generate(analysis)
        assert result is None

    def test_generate_returns_none_on_exception(self, tmp_path: Path, sample_analysis_result):
        client = MagicMock()
        client.generate_flow_diagram.side_effect = Exception("fail")
        gen = FlowDiagramGenerator(client, output_dir=str(tmp_path))
        result = gen.generate(sample_analysis_result)
        assert result is None

    def test_generate_uses_api_architecture_context(self, tmp_path: Path):
        analysis = AnalysisResult(
            input_source="test",
            input_type="local",
            api_architecture=ApiArchitectureResult(api_style="REST", total_endpoints=3),
        )
        client = _mock_claude()
        gen = FlowDiagramGenerator(client, output_dir=str(tmp_path))
        with patch.object(gen, "_render_dot", return_value=tmp_path / "uf.svg"):
            gen.generate(analysis)

        call_arg = client.generate_flow_diagram.call_args[0][0]
        assert "REST" in call_arg or "api" in call_arg.lower()

    def test_generate_uses_business_logic_context(self, tmp_path: Path):
        from agentfier.models.analysis import WorkflowInfo
        analysis = AnalysisResult(
            input_source="test",
            input_type="local",
            business_logic=BusinessLogicResult(
                workflows=[WorkflowInfo(name="Checkout", steps=["Cart", "Pay", "Confirm"])]
            ),
        )
        client = _mock_claude()
        gen = FlowDiagramGenerator(client, output_dir=str(tmp_path))
        with patch.object(gen, "_render_dot", return_value=tmp_path / "uf.svg"):
            gen.generate(analysis)

        call_arg = client.generate_flow_diagram.call_args[0][0]
        assert "Checkout" in call_arg or "business" in call_arg.lower()

    def test_render_dot_saves_dot_on_graphviz_missing(self, tmp_path: Path):
        gen = FlowDiagramGenerator(_mock_claude(), output_dir=str(tmp_path))
        with patch.dict("sys.modules", {"graphviz": None}):
            result = gen._render_dot(SAMPLE_DOT, "user_flow")
        assert result.suffix == ".dot"

    def test_render_dot_saves_dot_on_render_error(self, tmp_path: Path):
        gen = FlowDiagramGenerator(_mock_claude(), output_dir=str(tmp_path))
        mock_gv = MagicMock()
        mock_gv.Source.return_value.render.side_effect = Exception("fail")
        with patch.dict("sys.modules", {"graphviz": mock_gv}):
            result = gen._render_dot(SAMPLE_DOT, "user_flow")
        assert result.suffix == ".dot"
        assert result.read_text() == SAMPLE_DOT
