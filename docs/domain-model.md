# Agentfier — Domain Model

All domain entities are Pydantic v2 models. This document covers the full entity graph.

---

## Entity Relationship Diagram

```
AnalysisResult
│
├── input_source: str             # GitHub URL / local path / "upload"
├── input_type: str               # "github" | "local" | "jar"
├── analyzed_at: datetime
│
├── tech_stack: TechStackResult?
│   ├── languages: [LanguageInfo]
│   │   ├── name: str
│   │   ├── version: str?
│   │   └── percentage: float     # 0–100
│   ├── frameworks: [FrameworkInfo]
│   │   ├── name: str
│   │   ├── version: str?
│   │   └── category: str?
│   ├── build_tools: [str]
│   ├── runtime_targets: [str]
│   └── confidence: float         # 0–1
│
├── dependencies: DependencyResult?
│   ├── direct: [DependencyInfo]
│   │   ├── name: str
│   │   ├── version: str?
│   │   ├── purpose: str?
│   │   └── license: str?
│   ├── transitive_count: int
│   ├── licenses: dict[str, [str]]  # license → [package names]
│   └── vulnerabilities: [VulnerabilityInfo]
│       ├── package: str
│       ├── severity: str           # "low"|"medium"|"high"|"critical"
│       └── description: str?
│
├── data_layer: DataLayerResult?
│   ├── databases: [DatabaseInfo]
│   │   ├── type: str               # "PostgreSQL"|"MySQL"|"MongoDB"...
│   │   ├── name: str
│   │   ├── version: str?
│   │   └── purpose: str?
│   ├── orms: [str]
│   ├── cache_layers: [CacheLayerInfo]
│   │   ├── type: str
│   │   └── purpose: str?
│   ├── message_queues: [MessageQueueInfo]
│   │   ├── type: str
│   │   └── purpose: str?
│   └── has_migrations: bool
│
├── integrations: IntegrationResult?
│   ├── external_apis: [ExternalApiInfo]
│   │   ├── name: str
│   │   ├── protocol: str?          # "REST"|"gRPC"|"GraphQL"...
│   │   ├── purpose: str?
│   │   └── auth_method: str?
│   ├── webhooks: [str]
│   ├── third_party_services: [ThirdPartyServiceInfo]
│   │   ├── name: str
│   │   └── category: str?
│   └── message_brokers: [MessageBrokerInfo]
│       ├── type: str               # "Kafka"|"RabbitMQ"|"NATS"...
│       └── topics: [str]
│
├── auth: AuthResult?
│   ├── methods: [str]              # "JWT"|"OAuth2"|"Form Login"...
│   ├── authorization_pattern: str  # "RBAC"|"ABAC"|"ACL"...
│   ├── identity_providers: [str]
│   ├── token_management: str
│   ├── permission_model: str
│   └── multi_tenant: bool
│
├── observability: ObservabilityResult?
│   ├── logging_framework: str
│   ├── log_format: str
│   ├── metrics_tools: [str]
│   ├── tracing_tools: [str]
│   ├── apm_tools: [str]
│   ├── error_tracking: [str]
│   └── health_checks: bool
│
├── api_architecture: ApiArchitectureResult?
│   ├── endpoints: [EndpointInfo]
│   │   ├── method: str             # "GET"|"POST"|"PUT"|"DELETE"...
│   │   ├── path: str
│   │   └── description: str?
│   ├── api_style: str              # "REST"|"GraphQL"|"gRPC"|"MVC"...
│   ├── rate_limiting: bool
│   ├── versioning_strategy: str
│   ├── documentation_format: str  # "OpenAPI"|"Spring REST Docs"...
│   └── total_endpoints: int
│
├── business_logic: BusinessLogicResult?
│   ├── domain_models: [DomainModelInfo]
│   │   ├── name: str
│   │   └── description: str?
│   ├── workflows: [WorkflowInfo]
│   │   ├── name: str
│   │   ├── description: str?
│   │   └── steps: [str]
│   ├── background_jobs: [BackgroundJobInfo]
│   │   ├── name: str
│   │   ├── schedule: str?
│   │   └── purpose: str?
│   ├── state_machines: [str]
│   └── event_patterns: [str]
│
├── infrastructure: InfrastructureResult?
│   ├── containerized: bool
│   ├── orchestration: str          # "Kubernetes"|"Docker Compose"...
│   ├── ci_cd_tools: [str]
│   ├── iac_tools: [str]
│   ├── environments: [str]
│   ├── scaling_strategy: str
│   └── secrets_management: str
│
├── security: SecurityResult?
│   ├── encryption_at_rest: bool
│   ├── encryption_in_transit: bool
│   ├── cors_configured: bool
│   ├── input_validation: str
│   ├── audit_logging: bool
│   ├── compliance_standards: [str]  # "GDPR"|"PCI-DSS"|"SOC2"...
│   └── security_headers: [str]
│
├── frontend: FrontendResult?
│   ├── framework: str              # "React"|"Vue"|"Thymeleaf"...
│   ├── version: str
│   ├── state_management: str
│   ├── routing_library: str
│   ├── component_library: str
│   ├── build_tool: str
│   └── has_ssr: bool
│
└── configuration: ConfigurationResult?
    ├── env_vars_count: int
    ├── config_formats: [str]       # "application.yml"|".env"...
    ├── feature_flags: str
    ├── multi_env_strategy: str
    ├── secrets_approach: str
    └── dynamic_config: bool
```

---

## Ingestion Entities

```
IngestResult
├── workspace_path: str
├── file_manifest: [FileInfo]
│   ├── path: str          # relative to workspace_path
│   ├── size: int          # bytes
│   └── extension: str
├── total_files: int
└── total_size_bytes: int
```

---

## Specification / Output Entities

```
AgentSpec
├── analysis: AnalysisResult
├── conversion_plan: ConversionPlan?
├── diagram_paths: dict[str, str]   # "context" → "/path/to/c4_context.svg"
└── api_documentation: str?         # Markdown string

ConversionPlan
├── agent_decomposition: [AgentDecomposition]
│   ├── name: str
│   ├── responsibilities: [str]
│   └── tools: [str]
├── communication_topology: str     # "hub-and-spoke"|"mesh"|"pipeline"
├── orchestration_pattern: str
├── migration_phases: [MigrationPhase]
│   ├── phase: str                  # "1"|"2"|"3"...
│   ├── description: str?
│   ├── tasks: [str]
│   └── risks: [str]
└── risk_assessment: str
```

---

## Enumerations

```python
class InputType(str, Enum):
    GITHUB = "github"
    LOCAL  = "local"
    JAR    = "jar"

class AnalysisStatus(str, Enum):
    PENDING    = "pending"
    RUNNING    = "running"
    COMPLETE   = "complete"
    FAILED     = "failed"

class DiagramLevel(str, Enum):
    CONTEXT   = "context"
    CONTAINER = "container"
    COMPONENT = "component"
```

---

## Validation Rules

| Field | Constraint |
|-------|-----------|
| `LanguageInfo.percentage` | `ge=0.0, le=100.0` |
| `TechStackResult.confidence` | `ge=0.0, le=1.0` |
| `AgentfierConfig.temperature` | `ge=0.0, le=1.0` |
| `AgentfierConfig.max_tokens` | `ge=1, le=32000` |
| `AgentfierConfig.max_file_size_mb` | `ge=1` |
| `AgentfierConfig.max_files_to_analyze` | `ge=1` |

All `Optional` dimension fields default to `None`, enabling partial analysis results.
