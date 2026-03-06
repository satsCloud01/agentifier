"""
Tests for all Pydantic models: analysis models, spec models, and enums.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from agentfier.models.enums import AnalysisStatus, DiagramLevel, InputType
from agentfier.models.analysis import (
    AnalysisResult,
    ApiArchitectureResult,
    AuthResult,
    BackgroundJobInfo,
    BusinessLogicResult,
    CacheLayerInfo,
    ConfigurationResult,
    DataLayerResult,
    DatabaseInfo,
    DependencyInfo,
    DependencyResult,
    DomainModelInfo,
    EndpointInfo,
    ExternalApiInfo,
    FileInfo,
    FrameworkInfo,
    FrontendResult,
    InfrastructureResult,
    IngestResult,
    IntegrationResult,
    LanguageInfo,
    MessageBrokerInfo,
    MessageQueueInfo,
    ObservabilityResult,
    SecurityResult,
    TechStackResult,
    ThirdPartyServiceInfo,
    VulnerabilityInfo,
    WorkflowInfo,
)
from agentfier.models.spec import AgentDecomposition, AgentSpec, ConversionPlan, MigrationPhase


# ===========================================================================
# Enums
# ===========================================================================


class TestInputType:
    def test_values(self):
        assert InputType.GITHUB == "github"
        assert InputType.JAR_WAR == "jar_war"
        assert InputType.LOCAL == "local"

    def test_all_members(self):
        assert set(InputType) == {InputType.GITHUB, InputType.JAR_WAR, InputType.LOCAL}

    def test_string_equality(self):
        assert InputType.GITHUB == "github"
        assert "github" == InputType.GITHUB


class TestAnalysisStatus:
    def test_values(self):
        assert AnalysisStatus.PENDING == "pending"
        assert AnalysisStatus.RUNNING == "running"
        assert AnalysisStatus.COMPLETED == "completed"
        assert AnalysisStatus.ERROR == "error"

    def test_all_members(self):
        assert len(list(AnalysisStatus)) == 4


class TestDiagramLevel:
    def test_values(self):
        assert DiagramLevel.CONTEXT == "context"
        assert DiagramLevel.CONTAINER == "container"
        assert DiagramLevel.COMPONENT == "component"

    def test_all_members(self):
        assert len(list(DiagramLevel)) == 3


# ===========================================================================
# FileInfo & IngestResult
# ===========================================================================


class TestFileInfo:
    def test_basic_creation(self):
        f = FileInfo(path="src/main.py", size=1024, extension=".py")
        assert f.path == "src/main.py"
        assert f.size == 1024
        assert f.extension == ".py"

    def test_required_fields(self):
        with pytest.raises(ValidationError):
            FileInfo()  # type: ignore


class TestIngestResult:
    def test_default_empty(self):
        r = IngestResult(workspace_path="/tmp/ws")
        assert r.total_files == 0
        assert r.total_size_bytes == 0
        assert r.file_manifest == []

    def test_with_manifest(self, sample_ingest_result):
        assert sample_ingest_result.total_files == 2
        assert sample_ingest_result.total_size_bytes == 80
        assert len(sample_ingest_result.file_manifest) == 2


# ===========================================================================
# Dimension 1: TechStack
# ===========================================================================


class TestLanguageInfo:
    def test_percentage_bounds(self):
        with pytest.raises(ValidationError):
            LanguageInfo(name="Python", percentage=-1.0)
        with pytest.raises(ValidationError):
            LanguageInfo(name="Python", percentage=101.0)

    def test_optional_fields(self):
        lang = LanguageInfo(name="Go")
        assert lang.version is None
        assert lang.percentage == 0.0


class TestTechStackResult:
    def test_defaults(self):
        r = TechStackResult()
        assert r.languages == []
        assert r.frameworks == []
        assert r.build_tools == []
        assert r.runtime_targets == []
        assert r.confidence == 0.0

    def test_confidence_bounds(self):
        with pytest.raises(ValidationError):
            TechStackResult(confidence=1.5)
        with pytest.raises(ValidationError):
            TechStackResult(confidence=-0.1)

    def test_full_result(self, sample_tech_stack):
        assert len(sample_tech_stack.languages) == 2
        assert sample_tech_stack.languages[0].name == "Python"
        assert sample_tech_stack.confidence == 0.9


# ===========================================================================
# Dimension 2: Dependencies
# ===========================================================================


class TestDependencyResult:
    def test_defaults(self):
        r = DependencyResult()
        assert r.direct == []
        assert r.transitive_count == 0
        assert r.vulnerabilities == []
        assert r.licenses == {}

    def test_vulnerability_severity(self, sample_dependency_result):
        vuln = sample_dependency_result.vulnerabilities[0]
        assert vuln.severity == "high"
        assert vuln.package == "old-pkg"

    def test_license_grouping(self, sample_dependency_result):
        assert "MIT" in sample_dependency_result.licenses
        assert len(sample_dependency_result.licenses["MIT"]) == 2


# ===========================================================================
# Dimension 3: DataLayer
# ===========================================================================


class TestDataLayerResult:
    def test_defaults(self):
        r = DataLayerResult()
        assert r.databases == []
        assert r.has_migrations is False

    def test_full_result(self, sample_data_layer):
        assert sample_data_layer.databases[0].type == "PostgreSQL"
        assert sample_data_layer.cache_layers[0].type == "Redis"
        assert sample_data_layer.has_migrations is True


# ===========================================================================
# Dimension 4: Integrations
# ===========================================================================


class TestIntegrationResult:
    def test_defaults(self):
        r = IntegrationResult()
        assert r.external_apis == []
        assert r.webhooks == []
        assert r.third_party_services == []
        assert r.message_brokers == []

    def test_message_broker_topics(self):
        mb = MessageBrokerInfo(type="Kafka", topics=["orders", "notifications"])
        assert len(mb.topics) == 2


# ===========================================================================
# Dimension 5: Auth
# ===========================================================================


class TestAuthResult:
    def test_defaults(self):
        r = AuthResult()
        assert r.methods == []
        assert r.multi_tenant is False

    def test_full_result(self, sample_auth):
        assert "JWT" in sample_auth.methods
        assert sample_auth.multi_tenant is True
        assert sample_auth.authorization_pattern == "RBAC"


# ===========================================================================
# Dimension 6: Observability
# ===========================================================================


class TestObservabilityResult:
    def test_defaults(self):
        r = ObservabilityResult()
        assert r.logging_framework == ""
        assert r.health_checks is False
        assert r.metrics_tools == []

    def test_full_result(self):
        r = ObservabilityResult(
            logging_framework="structlog",
            log_format="JSON",
            metrics_tools=["Prometheus"],
            tracing_tools=["Jaeger"],
            health_checks=True,
        )
        assert r.health_checks is True
        assert "Prometheus" in r.metrics_tools


# ===========================================================================
# Dimension 7: API Architecture
# ===========================================================================


class TestApiArchitectureResult:
    def test_defaults(self):
        r = ApiArchitectureResult()
        assert r.endpoints == []
        assert r.total_endpoints == 0
        assert r.rate_limiting is False

    def test_endpoint_info(self):
        ep = EndpointInfo(method="GET", path="/health")
        assert ep.method == "GET"
        assert ep.description is None

    def test_full_result(self, sample_api_architecture):
        assert sample_api_architecture.total_endpoints == 2
        assert sample_api_architecture.api_style == "REST"
        assert sample_api_architecture.rate_limiting is True


# ===========================================================================
# Dimension 8: Business Logic
# ===========================================================================


class TestBusinessLogicResult:
    def test_defaults(self):
        r = BusinessLogicResult()
        assert r.domain_models == []
        assert r.workflows == []
        assert r.state_machines == []

    def test_workflow_steps(self):
        wf = WorkflowInfo(name="Onboarding", steps=["Step1", "Step2"])
        assert len(wf.steps) == 2

    def test_background_job(self):
        job = BackgroundJobInfo(name="cleanup", schedule="0 0 * * *", purpose="Prune logs")
        assert job.schedule == "0 0 * * *"


# ===========================================================================
# Dimension 9: Infrastructure
# ===========================================================================


class TestInfrastructureResult:
    def test_defaults(self):
        r = InfrastructureResult()
        assert r.containerized is False
        assert r.ci_cd_tools == []

    def test_full_result(self):
        r = InfrastructureResult(
            containerized=True,
            orchestration="Kubernetes",
            ci_cd_tools=["GitHub Actions"],
            environments=["dev", "prod"],
        )
        assert r.containerized is True
        assert "GitHub Actions" in r.ci_cd_tools


# ===========================================================================
# Dimension 10: Security
# ===========================================================================


class TestSecurityResult:
    def test_defaults(self):
        r = SecurityResult()
        assert r.encryption_at_rest is False
        assert r.compliance_standards == []

    def test_full_result(self):
        r = SecurityResult(
            encryption_at_rest=True,
            encryption_in_transit=True,
            cors_configured=True,
            audit_logging=True,
            compliance_standards=["SOC2"],
        )
        assert r.encryption_at_rest is True
        assert "SOC2" in r.compliance_standards


# ===========================================================================
# Dimension 11: Frontend
# ===========================================================================


class TestFrontendResult:
    def test_defaults(self):
        r = FrontendResult()
        assert r.framework == ""
        assert r.has_ssr is False

    def test_full_result(self):
        r = FrontendResult(framework="React", version="18", has_ssr=True)
        assert r.framework == "React"
        assert r.has_ssr is True


# ===========================================================================
# Dimension 12: Configuration
# ===========================================================================


class TestConfigurationResult:
    def test_defaults(self):
        r = ConfigurationResult()
        assert r.env_vars_count == 0
        assert r.dynamic_config is False

    def test_full_result(self):
        r = ConfigurationResult(env_vars_count=10, dynamic_config=True, config_formats=[".env"])
        assert r.env_vars_count == 10
        assert r.dynamic_config is True


# ===========================================================================
# AnalysisResult (aggregate)
# ===========================================================================


class TestAnalysisResult:
    def test_required_fields(self):
        with pytest.raises(ValidationError):
            AnalysisResult()  # type: ignore

    def test_defaults_with_required(self):
        r = AnalysisResult(input_source="local", input_type="local")
        assert r.tech_stack is None
        assert r.dependencies is None
        assert isinstance(r.analyzed_at, datetime)

    def test_all_dimensions_populated(self, sample_analysis_result):
        a = sample_analysis_result
        assert a.tech_stack is not None
        assert a.dependencies is not None
        assert a.data_layer is not None
        assert a.auth is not None
        assert a.api_architecture is not None
        assert a.business_logic is not None
        assert a.observability is not None
        assert a.infrastructure is not None
        assert a.security is not None
        assert a.frontend is not None
        assert a.configuration is not None

    def test_partial_result(self):
        r = AnalysisResult(
            input_source="/tmp/project",
            input_type="local",
            tech_stack=TechStackResult(languages=[LanguageInfo(name="Rust", percentage=100.0)]),
        )
        assert r.tech_stack.languages[0].name == "Rust"
        assert r.dependencies is None

    def test_model_dump_roundtrip(self, sample_analysis_result):
        data = sample_analysis_result.model_dump()
        restored = AnalysisResult.model_validate(data)
        assert restored.input_source == sample_analysis_result.input_source
        assert restored.tech_stack.confidence == sample_analysis_result.tech_stack.confidence


# ===========================================================================
# Spec models (ConversionPlan, AgentSpec)
# ===========================================================================


class TestAgentDecomposition:
    def test_defaults(self):
        a = AgentDecomposition(name="MyAgent")
        assert a.responsibilities == []
        assert a.tools == []

    def test_full_agent(self):
        a = AgentDecomposition(
            name="Data Agent",
            responsibilities=["query DB"],
            tools=["sql_query"],
        )
        assert a.name == "Data Agent"
        assert "sql_query" in a.tools


class TestMigrationPhase:
    def test_creation(self):
        p = MigrationPhase(phase="1", tasks=["Deploy NATS"], risks=["Ordering"])
        assert p.phase == "1"
        assert len(p.tasks) == 1

    def test_optional_description(self):
        p = MigrationPhase(phase="2")
        assert p.description is None


class TestConversionPlan:
    def test_defaults(self):
        p = ConversionPlan()
        assert p.agent_decomposition == []
        assert p.migration_phases == []
        assert p.communication_topology == ""

    def test_full_plan(self, sample_conversion_plan):
        assert len(sample_conversion_plan.agent_decomposition) == 2
        assert len(sample_conversion_plan.migration_phases) == 1
        assert "Hub" in sample_conversion_plan.communication_topology

    def test_model_dump_roundtrip(self, sample_conversion_plan):
        data = sample_conversion_plan.model_dump()
        restored = ConversionPlan.model_validate(data)
        assert len(restored.agent_decomposition) == len(sample_conversion_plan.agent_decomposition)


class TestAgentSpec:
    def test_creation(self, sample_analysis_result, sample_conversion_plan):
        spec = AgentSpec(
            analysis=sample_analysis_result,
            conversion_plan=sample_conversion_plan,
            diagram_paths={"context": "/tmp/c4_context.svg"},
            api_documentation="# API Docs",
        )
        assert spec.analysis.input_type == "github"
        assert spec.conversion_plan.orchestration_pattern == "Supervisor agent with specialized workers"
        assert spec.diagram_paths["context"] == "/tmp/c4_context.svg"

    def test_optional_fields(self, sample_analysis_result):
        spec = AgentSpec(analysis=sample_analysis_result)
        assert spec.conversion_plan is None
        assert spec.diagram_paths == {}
        assert spec.api_documentation is None
