"""
Shared pytest fixtures for Agentfier test suite.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

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


# ---------------------------------------------------------------------------
# Temporary workspace fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_workspace(tmp_path: Path) -> Path:
    """Return a temporary directory pre-populated with sample files."""
    # Python source
    (tmp_path / "main.py").write_text("import fastapi\napp = fastapi.FastAPI()\n")
    (tmp_path / "models.py").write_text("from sqlalchemy import Column\nclass User: pass\n")
    (tmp_path / "requirements.txt").write_text("fastapi==0.100.0\nsqlalchemy==2.0.0\n")
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "sample"\n')
    (tmp_path / "Dockerfile").write_text("FROM python:3.12\nCMD uvicorn main:app\n")
    (tmp_path / ".env.example").write_text("DATABASE_URL=\nSECRET_KEY=\n")
    sub = tmp_path / "src"
    sub.mkdir()
    (sub / "auth.py").write_text("import jwt\nimport bcrypt\n")
    (sub / "api.py").write_text(
        '@router.get("/users")\ndef list_users(): pass\n'
        '@router.post("/users")\ndef create_user(): pass\n'
    )
    return tmp_path


@pytest.fixture
def minimal_workspace(tmp_path: Path) -> Path:
    """An empty workspace directory (no files)."""
    return tmp_path


# ---------------------------------------------------------------------------
# Model fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_ingest_result(tmp_workspace: Path) -> IngestResult:
    return IngestResult(
        workspace_path=str(tmp_workspace),
        file_manifest=[
            FileInfo(path="main.py", size=50, extension=".py"),
            FileInfo(path="requirements.txt", size=30, extension=".txt"),
        ],
        total_files=2,
        total_size_bytes=80,
    )


@pytest.fixture
def sample_tech_stack() -> TechStackResult:
    return TechStackResult(
        languages=[
            LanguageInfo(name="Python", version="3.12", percentage=80.0),
            LanguageInfo(name="TypeScript", version="5.3", percentage=20.0),
        ],
        frameworks=[
            FrameworkInfo(name="FastAPI", version="0.100.0", category="Web Framework")
        ],
        build_tools=["pip", "npm"],
        runtime_targets=["CPython 3.12"],
        confidence=0.9,
    )


@pytest.fixture
def sample_dependency_result() -> DependencyResult:
    return DependencyResult(
        direct=[
            DependencyInfo(name="fastapi", version="0.100.0", purpose="Web", license="MIT"),
            DependencyInfo(name="sqlalchemy", version="2.0.0", purpose="ORM", license="MIT"),
        ],
        transitive_count=42,
        licenses={"MIT": ["fastapi", "sqlalchemy"]},
        vulnerabilities=[
            VulnerabilityInfo(package="old-pkg", severity="high", description="CVE-2024-1234")
        ],
    )


@pytest.fixture
def sample_data_layer() -> DataLayerResult:
    return DataLayerResult(
        databases=[DatabaseInfo(type="PostgreSQL", name="primary", version="15", purpose="Main store")],
        orms=["SQLAlchemy"],
        cache_layers=[CacheLayerInfo(type="Redis", purpose="Session cache")],
        message_queues=[MessageQueueInfo(type="Kafka", purpose="Event streaming")],
        has_migrations=True,
    )


@pytest.fixture
def sample_auth() -> AuthResult:
    return AuthResult(
        methods=["JWT", "OAuth2"],
        authorization_pattern="RBAC",
        identity_providers=["Auth0"],
        token_management="JWT with refresh tokens",
        permission_model="Role-based with scopes",
        multi_tenant=True,
    )


@pytest.fixture
def sample_api_architecture() -> ApiArchitectureResult:
    return ApiArchitectureResult(
        endpoints=[
            EndpointInfo(method="GET", path="/users", description="List users"),
            EndpointInfo(method="POST", path="/users", description="Create user"),
        ],
        api_style="REST",
        rate_limiting=True,
        versioning_strategy="URL prefix /v1",
        documentation_format="OpenAPI",
        total_endpoints=2,
    )


@pytest.fixture
def sample_business_logic() -> BusinessLogicResult:
    return BusinessLogicResult(
        domain_models=[DomainModelInfo(name="User", description="Application user")],
        workflows=[WorkflowInfo(name="Onboarding", description="User onboarding", steps=["Register", "Verify", "Activate"])],
        background_jobs=[BackgroundJobInfo(name="cleanup", schedule="daily", purpose="Remove stale sessions")],
        state_machines=["OrderStateMachine"],
        event_patterns=["pub/sub"],
    )


@pytest.fixture
def sample_analysis_result(
    sample_tech_stack,
    sample_dependency_result,
    sample_data_layer,
    sample_auth,
    sample_api_architecture,
    sample_business_logic,
) -> AnalysisResult:
    return AnalysisResult(
        input_source="https://github.com/example/repo",
        input_type="github",
        tech_stack=sample_tech_stack,
        dependencies=sample_dependency_result,
        data_layer=sample_data_layer,
        integrations=IntegrationResult(
            external_apis=[ExternalApiInfo(name="Stripe", protocol="REST", purpose="Payments")],
            third_party_services=[ThirdPartyServiceInfo(name="SendGrid", category="Email")],
            message_brokers=[MessageBrokerInfo(type="Kafka", topics=["orders"])],
        ),
        auth=sample_auth,
        api_architecture=sample_api_architecture,
        business_logic=sample_business_logic,
        observability=ObservabilityResult(
            logging_framework="structlog",
            log_format="JSON",
            metrics_tools=["Prometheus"],
            tracing_tools=["Jaeger"],
            health_checks=True,
        ),
        infrastructure=InfrastructureResult(
            containerized=True,
            orchestration="Kubernetes",
            ci_cd_tools=["GitHub Actions"],
            iac_tools=["Terraform"],
            environments=["dev", "staging", "prod"],
            scaling_strategy="Horizontal pod autoscaler",
        ),
        security=SecurityResult(
            encryption_at_rest=True,
            encryption_in_transit=True,
            cors_configured=True,
            input_validation="Pydantic",
            audit_logging=True,
            compliance_standards=["SOC2", "GDPR"],
            security_headers=["HSTS", "CSP"],
        ),
        frontend=FrontendResult(
            framework="React",
            version="18",
            state_management="Redux",
            routing_library="React Router",
            component_library="Tailwind",
            build_tool="Vite",
            has_ssr=False,
        ),
        configuration=ConfigurationResult(
            env_vars_count=12,
            config_formats=[".env", "YAML"],
            feature_flags="LaunchDarkly",
            multi_env_strategy="Per-environment .env files",
            secrets_approach="AWS Secrets Manager",
            dynamic_config=True,
        ),
    )


@pytest.fixture
def sample_conversion_plan() -> ConversionPlan:
    return ConversionPlan(
        agent_decomposition=[
            AgentDecomposition(
                name="Data Agent",
                responsibilities=["DB queries", "cache management"],
                tools=["sql_query", "cache_get"],
            ),
            AgentDecomposition(
                name="API Gateway Agent",
                responsibilities=["Request routing"],
                tools=["route_request"],
            ),
        ],
        communication_topology="Hub-and-spoke with message bus",
        orchestration_pattern="Supervisor agent with specialized workers",
        migration_phases=[
            MigrationPhase(
                phase="1",
                description="Foundation",
                tasks=["Deploy NATS", "Create agent base classes"],
                risks=["Message ordering"],
            )
        ],
        risk_assessment="Medium risk - established patterns available",
    )


@pytest.fixture
def mock_claude_client():
    """A mock ClaudeClient that returns deterministic JSON."""
    client = MagicMock()
    client.analyze.return_value = {
        "languages": [{"name": "Python", "version": "3.12", "percentage": 100.0}],
        "frameworks": [{"name": "FastAPI", "version": "0.100.0", "category": "Web"}],
        "build_tools": ["pip"],
        "runtime_targets": ["CPython 3.12"],
        "confidence": 0.85,
    }
    return client
