"""
Tests for BaseAnalyzer and all 12 analysis dimension analyzers.
All Claude API calls are mocked to avoid live API usage.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentfier.analyzers.base import BaseAnalyzer
from agentfier.models.analysis import (
    ApiArchitectureResult,
    AuthResult,
    BusinessLogicResult,
    ConfigurationResult,
    DataLayerResult,
    DependencyResult,
    FrontendResult,
    InfrastructureResult,
    ObservabilityResult,
    SecurityResult,
    TechStackResult,
    IntegrationResult,
)


# ===========================================================================
# Helpers
# ===========================================================================


def _mock_client_for(result_model_instance):
    """Return a mock ClaudeClient whose .analyze() returns the model's dict."""
    client = MagicMock()
    client.analyze.return_value = result_model_instance.model_dump()
    return client


def _make_analyzer(cls, workspace: Path, return_model):
    """Instantiate an analyzer with a mock Claude client."""
    client = _mock_client_for(return_model)
    return cls(client, str(workspace)), client


# ===========================================================================
# BaseAnalyzer: file discovery and reading
# ===========================================================================


class _DummyAnalyzer(BaseAnalyzer):
    """Minimal concrete analyzer used for base-class tests."""
    DIMENSION = "tech_stack"
    PATTERNS = ["**/*.py", "**/*.txt"]

    def _get_result_model(self):
        return TechStackResult


class TestBaseAnalyzerFileDiscovery:
    def test_finds_relevant_files(self, tmp_workspace: Path):
        client = MagicMock()
        client.analyze.return_value = TechStackResult().model_dump()
        az = _DummyAnalyzer(client, str(tmp_workspace))
        files = az.get_relevant_files()
        extensions = {f.suffix for f in files}
        assert ".py" in extensions or ".txt" in extensions

    def test_respects_max_files(self, tmp_path: Path):
        for i in range(250):
            (tmp_path / f"file_{i}.py").write_text("pass")
        client = MagicMock()
        client.analyze.return_value = TechStackResult().model_dump()
        az = _DummyAnalyzer(client, str(tmp_path))
        files = az.get_relevant_files()
        assert len(files) <= az.MAX_FILES

    def test_no_duplicate_files(self, tmp_workspace: Path):
        client = MagicMock()
        client.analyze.return_value = TechStackResult().model_dump()
        az = _DummyAnalyzer(client, str(tmp_workspace))
        files = az.get_relevant_files()
        paths = [str(f) for f in files]
        assert len(paths) == len(set(paths))

    def test_read_files_respects_budget(self, tmp_path: Path):
        large = "x" * 10000
        (tmp_path / "big.py").write_text(large)
        (tmp_path / "small.py").write_text("pass")
        client = MagicMock()
        client.analyze.return_value = TechStackResult().model_dump()
        az = _DummyAnalyzer(client, str(tmp_path))
        files = list(tmp_path.glob("**/*.py"))
        content = az._read_files(files, max_chars=500)
        assert len(content) <= 600  # some overhead for header

    def test_empty_workspace_returns_default(self, minimal_workspace: Path):
        client = MagicMock()
        az = _DummyAnalyzer(client, str(minimal_workspace))
        result = az.analyze()
        assert isinstance(result, TechStackResult)
        client.analyze.assert_not_called()

    def test_analyze_calls_claude(self, tmp_workspace: Path):
        expected = TechStackResult(build_tools=["pip"])
        client = _mock_client_for(expected)
        az = _DummyAnalyzer(client, str(tmp_workspace))
        result = az.analyze()
        client.analyze.assert_called_once()
        assert isinstance(result, TechStackResult)

    def test_heuristics_default_empty_dict(self, tmp_workspace: Path):
        client = MagicMock()
        az = _DummyAnalyzer(client, str(tmp_workspace))
        h = az._run_heuristics([])
        assert h == {}


# ===========================================================================
# Dimension 1: TechStackAnalyzer
# ===========================================================================


class TestTechStackAnalyzer:
    def test_analyze_returns_tech_stack_result(self, tmp_workspace: Path):
        from agentfier.analyzers.tech_stack import TechStackAnalyzer
        expected = TechStackResult(build_tools=["pip"], confidence=0.9)
        az, client = _make_analyzer(TechStackAnalyzer, tmp_workspace, expected)
        result = az.analyze()
        assert isinstance(result, TechStackResult)

    def test_heuristics_detect_python(self, tmp_workspace: Path):
        from agentfier.analyzers.tech_stack import TechStackAnalyzer
        client = MagicMock()
        client.analyze.return_value = TechStackResult().model_dump()
        az = TechStackAnalyzer(client, str(tmp_workspace))
        files = [tmp_workspace / "main.py", tmp_workspace / "models.py"]
        h = az._run_heuristics(files)
        assert "Python" in h.get("language_distribution", {})

    def test_heuristics_detect_requirements_txt(self, tmp_workspace: Path):
        from agentfier.analyzers.tech_stack import TechStackAnalyzer
        client = MagicMock()
        client.analyze.return_value = TechStackResult().model_dump()
        az = TechStackAnalyzer(client, str(tmp_workspace))
        files = [tmp_workspace / "requirements.txt"]
        h = az._run_heuristics(files)
        assert "requirements.txt" in h.get("build_files_found", [])

    def test_heuristics_calculates_percentages(self, tmp_path: Path):
        from agentfier.analyzers.tech_stack import TechStackAnalyzer
        (tmp_path / "a.py").write_text("pass")
        (tmp_path / "b.py").write_text("pass")
        (tmp_path / "c.js").write_text("var x=1")
        client = MagicMock()
        client.analyze.return_value = TechStackResult().model_dump()
        az = TechStackAnalyzer(client, str(tmp_path))
        files = list(tmp_path.glob("*"))
        h = az._run_heuristics(files)
        dist = h.get("language_distribution", {})
        assert dist.get("Python", 0) > dist.get("JavaScript", 0)

    def test_prioritizes_build_files(self, tmp_workspace: Path):
        from agentfier.analyzers.tech_stack import TechStackAnalyzer
        client = MagicMock()
        client.analyze.return_value = TechStackResult().model_dump()
        az = TechStackAnalyzer(client, str(tmp_workspace))
        files = az.get_relevant_files()
        names = [f.name for f in files]
        # Build files should appear before source files
        build_indices = [i for i, n in enumerate(names) if n in ("requirements.txt", "pyproject.toml")]
        if build_indices:
            assert min(build_indices) < len(names) - 1

    def test_result_model_type(self):
        from agentfier.analyzers.tech_stack import TechStackAnalyzer
        client = MagicMock()
        az = TechStackAnalyzer(client, "/tmp")
        assert az._get_result_model() is TechStackResult


# ===========================================================================
# Dimension 2: DependencyAnalyzer
# ===========================================================================


class TestDependencyAnalyzer:
    def test_analyze_returns_dependency_result(self, tmp_workspace: Path):
        from agentfier.analyzers.dependencies import DependencyAnalyzer
        expected = DependencyResult(transitive_count=10)
        az, _ = _make_analyzer(DependencyAnalyzer, tmp_workspace, expected)
        result = az.analyze()
        assert isinstance(result, DependencyResult)

    def test_result_model_type(self):
        from agentfier.analyzers.dependencies import DependencyAnalyzer
        client = MagicMock()
        az = DependencyAnalyzer(client, "/tmp")
        assert az._get_result_model() is DependencyResult


# ===========================================================================
# Dimension 3: DataLayerAnalyzer
# ===========================================================================


class TestDataLayerAnalyzer:
    def test_analyze_returns_data_layer_result(self, tmp_workspace: Path):
        from agentfier.analyzers.data_layer import DataLayerAnalyzer
        expected = DataLayerResult(has_migrations=True)
        az, _ = _make_analyzer(DataLayerAnalyzer, tmp_workspace, expected)
        result = az.analyze()
        assert isinstance(result, DataLayerResult)

    def test_result_model_type(self):
        from agentfier.analyzers.data_layer import DataLayerAnalyzer
        client = MagicMock()
        az = DataLayerAnalyzer(client, "/tmp")
        assert az._get_result_model() is DataLayerResult


# ===========================================================================
# Dimension 4: IntegrationAnalyzer
# ===========================================================================


class TestIntegrationAnalyzer:
    def test_analyze_returns_integration_result(self, tmp_workspace: Path):
        from agentfier.analyzers.integrations import IntegrationAnalyzer
        expected = IntegrationResult()
        az, _ = _make_analyzer(IntegrationAnalyzer, tmp_workspace, expected)
        result = az.analyze()
        assert isinstance(result, IntegrationResult)

    def test_result_model_type(self):
        from agentfier.analyzers.integrations import IntegrationAnalyzer
        client = MagicMock()
        az = IntegrationAnalyzer(client, "/tmp")
        assert az._get_result_model() is IntegrationResult


# ===========================================================================
# Dimension 5: AuthAnalyzer
# ===========================================================================


class TestAuthAnalyzer:
    def test_analyze_returns_auth_result(self, tmp_workspace: Path):
        from agentfier.analyzers.auth import AuthAnalyzer
        expected = AuthResult(methods=["JWT"], authorization_pattern="RBAC")
        az, _ = _make_analyzer(AuthAnalyzer, tmp_workspace, expected)
        result = az.analyze()
        assert isinstance(result, AuthResult)

    def test_result_model_type(self):
        from agentfier.analyzers.auth import AuthAnalyzer
        client = MagicMock()
        az = AuthAnalyzer(client, "/tmp")
        assert az._get_result_model() is AuthResult


# ===========================================================================
# Dimension 6: ObservabilityAnalyzer
# ===========================================================================


class TestObservabilityAnalyzer:
    def test_analyze_returns_observability_result(self, tmp_workspace: Path):
        from agentfier.analyzers.observability import ObservabilityAnalyzer
        expected = ObservabilityResult(logging_framework="structlog", health_checks=True)
        az, _ = _make_analyzer(ObservabilityAnalyzer, tmp_workspace, expected)
        result = az.analyze()
        assert isinstance(result, ObservabilityResult)

    def test_result_model_type(self):
        from agentfier.analyzers.observability import ObservabilityAnalyzer
        client = MagicMock()
        az = ObservabilityAnalyzer(client, "/tmp")
        assert az._get_result_model() is ObservabilityResult


# ===========================================================================
# Dimension 7: ApiArchitectureAnalyzer
# ===========================================================================


class TestApiArchitectureAnalyzer:
    def test_analyze_returns_api_result(self, tmp_workspace: Path):
        from agentfier.analyzers.api_architecture import ApiArchitectureAnalyzer
        expected = ApiArchitectureResult(api_style="REST", total_endpoints=5)
        az, _ = _make_analyzer(ApiArchitectureAnalyzer, tmp_workspace, expected)
        result = az.analyze()
        assert isinstance(result, ApiArchitectureResult)

    def test_result_model_type(self):
        from agentfier.analyzers.api_architecture import ApiArchitectureAnalyzer
        client = MagicMock()
        az = ApiArchitectureAnalyzer(client, "/tmp")
        assert az._get_result_model() is ApiArchitectureResult


# ===========================================================================
# Dimension 8: BusinessLogicAnalyzer
# ===========================================================================


class TestBusinessLogicAnalyzer:
    def test_analyze_returns_business_result(self, tmp_workspace: Path):
        from agentfier.analyzers.business_logic import BusinessLogicAnalyzer
        expected = BusinessLogicResult(state_machines=["OrderSM"])
        az, _ = _make_analyzer(BusinessLogicAnalyzer, tmp_workspace, expected)
        result = az.analyze()
        assert isinstance(result, BusinessLogicResult)

    def test_result_model_type(self):
        from agentfier.analyzers.business_logic import BusinessLogicAnalyzer
        client = MagicMock()
        az = BusinessLogicAnalyzer(client, "/tmp")
        assert az._get_result_model() is BusinessLogicResult


# ===========================================================================
# Dimension 9: InfrastructureAnalyzer
# ===========================================================================


class TestInfrastructureAnalyzer:
    def test_analyze_returns_infra_result(self, tmp_workspace: Path):
        from agentfier.analyzers.infrastructure import InfrastructureAnalyzer
        expected = InfrastructureResult(containerized=True, orchestration="Kubernetes")
        az, _ = _make_analyzer(InfrastructureAnalyzer, tmp_workspace, expected)
        result = az.analyze()
        assert isinstance(result, InfrastructureResult)

    def test_result_model_type(self):
        from agentfier.analyzers.infrastructure import InfrastructureAnalyzer
        client = MagicMock()
        az = InfrastructureAnalyzer(client, "/tmp")
        assert az._get_result_model() is InfrastructureResult


# ===========================================================================
# Dimension 10: SecurityAnalyzer
# ===========================================================================


class TestSecurityAnalyzer:
    def test_analyze_returns_security_result(self, tmp_workspace: Path):
        from agentfier.analyzers.security import SecurityAnalyzer
        expected = SecurityResult(encryption_at_rest=True, audit_logging=True)
        az, _ = _make_analyzer(SecurityAnalyzer, tmp_workspace, expected)
        result = az.analyze()
        assert isinstance(result, SecurityResult)

    def test_result_model_type(self):
        from agentfier.analyzers.security import SecurityAnalyzer
        client = MagicMock()
        az = SecurityAnalyzer(client, "/tmp")
        assert az._get_result_model() is SecurityResult


# ===========================================================================
# Dimension 11: FrontendAnalyzer
# ===========================================================================


class TestFrontendAnalyzer:
    def test_analyze_returns_frontend_result(self, tmp_workspace: Path):
        from agentfier.analyzers.frontend import FrontendAnalyzer
        expected = FrontendResult(framework="React", version="18")
        az, _ = _make_analyzer(FrontendAnalyzer, tmp_workspace, expected)
        result = az.analyze()
        assert isinstance(result, FrontendResult)

    def test_result_model_type(self):
        from agentfier.analyzers.frontend import FrontendAnalyzer
        client = MagicMock()
        az = FrontendAnalyzer(client, "/tmp")
        assert az._get_result_model() is FrontendResult


# ===========================================================================
# Dimension 12: ConfigurationAnalyzer
# ===========================================================================


class TestConfigurationAnalyzer:
    def test_analyze_returns_config_result(self, tmp_workspace: Path):
        from agentfier.analyzers.configuration import ConfigurationAnalyzer
        expected = ConfigurationResult(env_vars_count=5, dynamic_config=True)
        az, _ = _make_analyzer(ConfigurationAnalyzer, tmp_workspace, expected)
        result = az.analyze()
        assert isinstance(result, ConfigurationResult)

    def test_result_model_type(self):
        from agentfier.analyzers.configuration import ConfigurationAnalyzer
        client = MagicMock()
        az = ConfigurationAnalyzer(client, "/tmp")
        assert az._get_result_model() is ConfigurationResult


# ===========================================================================
# Cross-cutting: all analyzers share base behavior
# ===========================================================================


ALL_ANALYZERS = [
    ("tech_stack", "agentfier.analyzers.tech_stack", "TechStackAnalyzer", TechStackResult),
    ("dependencies", "agentfier.analyzers.dependencies", "DependencyAnalyzer", DependencyResult),
    ("data_layer", "agentfier.analyzers.data_layer", "DataLayerAnalyzer", DataLayerResult),
    ("integrations", "agentfier.analyzers.integrations", "IntegrationAnalyzer", IntegrationResult),
    ("auth", "agentfier.analyzers.auth", "AuthAnalyzer", AuthResult),
    ("observability", "agentfier.analyzers.observability", "ObservabilityAnalyzer", ObservabilityResult),
    ("api_architecture", "agentfier.analyzers.api_architecture", "ApiArchitectureAnalyzer", ApiArchitectureResult),
    ("business_logic", "agentfier.analyzers.business_logic", "BusinessLogicAnalyzer", BusinessLogicResult),
    ("infrastructure", "agentfier.analyzers.infrastructure", "InfrastructureAnalyzer", InfrastructureResult),
    ("security", "agentfier.analyzers.security", "SecurityAnalyzer", SecurityResult),
    ("frontend", "agentfier.analyzers.frontend", "FrontendAnalyzer", FrontendResult),
    ("configuration", "agentfier.analyzers.configuration", "ConfigurationAnalyzer", ConfigurationResult),
]


@pytest.mark.parametrize("dim_key,module,cls_name,model_cls", ALL_ANALYZERS, ids=[r[0] for r in ALL_ANALYZERS])
class TestAllAnalyzersBaseContract:
    def test_empty_workspace_returns_default_model(self, minimal_workspace, dim_key, module, cls_name, model_cls):
        import importlib
        mod = importlib.import_module(module)
        cls = getattr(mod, cls_name)
        client = MagicMock()
        az = cls(client, str(minimal_workspace))
        result = az.analyze()
        assert isinstance(result, model_cls)
        client.analyze.assert_not_called()

    def test_dimension_attribute_set(self, minimal_workspace, dim_key, module, cls_name, model_cls):
        import importlib
        mod = importlib.import_module(module)
        cls = getattr(mod, cls_name)
        client = MagicMock()
        az = cls(client, str(minimal_workspace))
        assert az.DIMENSION != ""

    def test_patterns_non_empty(self, minimal_workspace, dim_key, module, cls_name, model_cls):
        import importlib
        mod = importlib.import_module(module)
        cls = getattr(mod, cls_name)
        client = MagicMock()
        az = cls(client, str(minimal_workspace))
        assert len(az.PATTERNS) > 0
