"""
Agentfier analysis models.

Comprehensive Pydantic models covering all 12 analysis dimensions plus
ingestion results and the top-level ``AnalysisResult`` aggregate.
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# =====================================================================
# Shared / helper sub-models
# =====================================================================


class FileInfo(BaseModel):
    """Metadata for a single file discovered during ingestion."""

    path: str
    size: int
    extension: str


# =====================================================================
# Ingestion result
# =====================================================================


class IngestResult(BaseModel):
    """Output produced by the ingestion stage."""

    workspace_path: str
    file_manifest: List[FileInfo] = Field(default_factory=list)
    total_files: int = 0
    total_size_bytes: int = 0


# =====================================================================
# 1. Tech Stack
# =====================================================================


class LanguageInfo(BaseModel):
    name: str
    version: Optional[str] = None
    percentage: float = Field(
        default=0.0, ge=0.0, le=100.0, description="Percentage of codebase"
    )


class FrameworkInfo(BaseModel):
    name: str
    version: Optional[str] = None
    category: Optional[str] = None


class TechStackResult(BaseModel):
    """Dimension 1 -- Programming languages, frameworks, and build tooling."""

    languages: List[LanguageInfo] = Field(default_factory=list)
    frameworks: List[FrameworkInfo] = Field(default_factory=list)
    build_tools: List[str] = Field(default_factory=list)
    runtime_targets: List[str] = Field(default_factory=list)
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Confidence score 0-1"
    )


# =====================================================================
# 2. Dependencies
# =====================================================================


class DependencyInfo(BaseModel):
    name: str
    version: Optional[str] = None
    purpose: Optional[str] = None
    license: Optional[str] = None


class VulnerabilityInfo(BaseModel):
    package: str
    severity: str
    description: Optional[str] = None


class DependencyResult(BaseModel):
    """Dimension 2 -- Direct / transitive dependencies, licences, and CVEs."""

    direct: List[DependencyInfo] = Field(default_factory=list)
    transitive_count: int = 0
    licenses: Dict[str, List[str]] = Field(default_factory=dict)
    vulnerabilities: List[VulnerabilityInfo] = Field(default_factory=list)


# =====================================================================
# 3. Data Layer
# =====================================================================


class DatabaseInfo(BaseModel):
    type: str
    name: str
    version: Optional[str] = None
    purpose: Optional[str] = None


class CacheLayerInfo(BaseModel):
    type: str
    purpose: Optional[str] = None


class MessageQueueInfo(BaseModel):
    type: str
    purpose: Optional[str] = None


class DataLayerResult(BaseModel):
    """Dimension 3 -- Databases, ORMs, caches, and message queues."""

    databases: List[DatabaseInfo] = Field(default_factory=list)
    orms: List[str] = Field(default_factory=list)
    cache_layers: List[CacheLayerInfo] = Field(default_factory=list)
    message_queues: List[MessageQueueInfo] = Field(default_factory=list)
    has_migrations: bool = False


# =====================================================================
# 4. Integrations
# =====================================================================


class ExternalApiInfo(BaseModel):
    name: str
    protocol: Optional[str] = None
    purpose: Optional[str] = None
    auth_method: Optional[str] = None


class ThirdPartyServiceInfo(BaseModel):
    name: str
    category: Optional[str] = None


class MessageBrokerInfo(BaseModel):
    type: str
    topics: List[str] = Field(default_factory=list)


class IntegrationResult(BaseModel):
    """Dimension 4 -- External APIs, webhooks, and third-party services."""

    external_apis: List[ExternalApiInfo] = Field(default_factory=list)
    webhooks: List[str] = Field(default_factory=list)
    third_party_services: List[ThirdPartyServiceInfo] = Field(default_factory=list)
    message_brokers: List[MessageBrokerInfo] = Field(default_factory=list)


# =====================================================================
# 5. Authentication & Authorization
# =====================================================================


class AuthResult(BaseModel):
    """Dimension 5 -- Authentication methods, authorization patterns, IdPs."""

    methods: List[str] = Field(default_factory=list)
    authorization_pattern: str = ""
    identity_providers: List[str] = Field(default_factory=list)
    token_management: str = ""
    permission_model: str = ""
    multi_tenant: bool = False


# =====================================================================
# 6. Observability
# =====================================================================


class ObservabilityResult(BaseModel):
    """Dimension 6 -- Logging, metrics, tracing, APM, and error tracking."""

    logging_framework: str = ""
    log_format: str = ""
    metrics_tools: List[str] = Field(default_factory=list)
    tracing_tools: List[str] = Field(default_factory=list)
    apm_tools: List[str] = Field(default_factory=list)
    error_tracking: List[str] = Field(default_factory=list)
    health_checks: bool = False


# =====================================================================
# 7. API Architecture
# =====================================================================


class EndpointInfo(BaseModel):
    method: str
    path: str
    description: Optional[str] = None


class ApiArchitectureResult(BaseModel):
    """Dimension 7 -- Endpoints, API style, rate limiting, versioning."""

    endpoints: List[EndpointInfo] = Field(default_factory=list)
    api_style: str = ""
    rate_limiting: bool = False
    versioning_strategy: str = ""
    documentation_format: str = ""
    total_endpoints: int = 0


# =====================================================================
# 8. Business Logic
# =====================================================================


class DomainModelInfo(BaseModel):
    name: str
    description: Optional[str] = None


class WorkflowInfo(BaseModel):
    name: str
    description: Optional[str] = None
    steps: List[str] = Field(default_factory=list)


class BackgroundJobInfo(BaseModel):
    name: str
    schedule: Optional[str] = None
    purpose: Optional[str] = None


class BusinessLogicResult(BaseModel):
    """Dimension 8 -- Domain models, workflows, background jobs, events."""

    domain_models: List[DomainModelInfo] = Field(default_factory=list)
    workflows: List[WorkflowInfo] = Field(default_factory=list)
    background_jobs: List[BackgroundJobInfo] = Field(default_factory=list)
    state_machines: List[str] = Field(default_factory=list)
    event_patterns: List[str] = Field(default_factory=list)


# =====================================================================
# 9. Infrastructure
# =====================================================================


class InfrastructureResult(BaseModel):
    """Dimension 9 -- Containers, CI/CD, IaC, environments, scaling."""

    containerized: bool = False
    orchestration: str = ""
    ci_cd_tools: List[str] = Field(default_factory=list)
    iac_tools: List[str] = Field(default_factory=list)
    environments: List[str] = Field(default_factory=list)
    scaling_strategy: str = ""
    secrets_management: str = ""


# =====================================================================
# 10. Security
# =====================================================================


class SecurityResult(BaseModel):
    """Dimension 10 -- Encryption, CORS, validation, compliance."""

    encryption_at_rest: bool = False
    encryption_in_transit: bool = False
    cors_configured: bool = False
    input_validation: str = ""
    audit_logging: bool = False
    compliance_standards: List[str] = Field(default_factory=list)
    security_headers: List[str] = Field(default_factory=list)


# =====================================================================
# 11. Frontend
# =====================================================================


class FrontendResult(BaseModel):
    """Dimension 11 -- Frontend framework, state management, SSR."""

    framework: str = ""
    version: str = ""
    state_management: str = ""
    routing_library: str = ""
    component_library: str = ""
    build_tool: str = ""
    has_ssr: bool = False


# =====================================================================
# 12. Configuration
# =====================================================================


class ConfigurationResult(BaseModel):
    """Dimension 12 -- Environment variables, feature flags, config strategy."""

    env_vars_count: int = 0
    config_formats: List[str] = Field(default_factory=list)
    feature_flags: str = ""
    multi_env_strategy: str = ""
    secrets_approach: str = ""
    dynamic_config: bool = False


# =====================================================================
# Top-level aggregate
# =====================================================================


class AnalysisResult(BaseModel):
    """Aggregate result containing the source metadata and all 12 dimension
    analysis outputs.  Each dimension field is ``Optional`` and defaults to
    ``None`` so that partial results can be represented.
    """

    # Source metadata
    input_source: str
    input_type: str
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)

    # Dimension results (all optional)
    tech_stack: Optional[TechStackResult] = None
    dependencies: Optional[DependencyResult] = None
    data_layer: Optional[DataLayerResult] = None
    integrations: Optional[IntegrationResult] = None
    auth: Optional[AuthResult] = None
    observability: Optional[ObservabilityResult] = None
    api_architecture: Optional[ApiArchitectureResult] = None
    business_logic: Optional[BusinessLogicResult] = None
    infrastructure: Optional[InfrastructureResult] = None
    security: Optional[SecurityResult] = None
    frontend: Optional[FrontendResult] = None
    configuration: Optional[ConfigurationResult] = None
