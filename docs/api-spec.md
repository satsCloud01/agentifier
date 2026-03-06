# Agentfier — Python Module API Specification

All public interfaces in the `agentfier` package, organized by module.

---

## `agentfier.config`

```python
class AgentfierConfig(BaseSettings):
    """Application configuration loaded from environment variables.
    All fields have defaults except api_key."""

    api_key: str                                # ANTHROPIC_API_KEY (required)
    model: str = "claude-sonnet-4-6"            # CLAUDE_MODEL
    max_tokens: int = 4096                      # MAX_TOKENS (1–32000)
    temperature: float = 0.2                    # TEMPERATURE (0.0–1.0)
    cfr_jar_path: str = "tools/cfr.jar"         # CFR_JAR_PATH
    workspace_dir: str = "data/workspaces"      # WORKSPACE_DIR
    output_dir: str = "data/outputs"            # OUTPUT_DIR
    max_file_size_mb: int = 100                 # MAX_FILE_SIZE_MB
    max_files_to_analyze: int = 500             # MAX_FILES_TO_ANALYZE

    @property
    def workspace_path(self) -> Path: ...
    @property
    def output_path(self) -> Path: ...
    @property
    def cfr_jar(self) -> Path: ...
    @property
    def max_file_size_bytes(self) -> int: ...
```

---

## `agentfier.models.analysis`

### Sub-models (all Pydantic `BaseModel`)

```python
class FileInfo(BaseModel):
    path: str; size: int; extension: str

class IngestResult(BaseModel):
    workspace_path: str
    file_manifest: list[FileInfo] = []
    total_files: int = 0
    total_size_bytes: int = 0

class LanguageInfo(BaseModel):
    name: str; version: str | None = None
    percentage: float = Field(0.0, ge=0.0, le=100.0)

class FrameworkInfo(BaseModel):
    name: str; version: str | None = None; category: str | None = None

class TechStackResult(BaseModel):
    languages: list[LanguageInfo] = []
    frameworks: list[FrameworkInfo] = []
    build_tools: list[str] = []
    runtime_targets: list[str] = []
    confidence: float = Field(0.0, ge=0.0, le=1.0)

class DependencyInfo(BaseModel):
    name: str; version: str | None = None
    purpose: str | None = None; license: str | None = None

class VulnerabilityInfo(BaseModel):
    package: str; severity: str; description: str | None = None

class DependencyResult(BaseModel):
    direct: list[DependencyInfo] = []
    transitive_count: int = 0
    licenses: dict[str, list[str]] = {}
    vulnerabilities: list[VulnerabilityInfo] = []

class DatabaseInfo(BaseModel):
    type: str; name: str; version: str | None = None; purpose: str | None = None

class CacheLayerInfo(BaseModel):
    type: str; purpose: str | None = None

class MessageQueueInfo(BaseModel):
    type: str; purpose: str | None = None

class DataLayerResult(BaseModel):
    databases: list[DatabaseInfo] = []
    orms: list[str] = []
    cache_layers: list[CacheLayerInfo] = []
    message_queues: list[MessageQueueInfo] = []
    has_migrations: bool = False

class ExternalApiInfo(BaseModel):
    name: str; protocol: str | None = None
    purpose: str | None = None; auth_method: str | None = None

class ThirdPartyServiceInfo(BaseModel):
    name: str; category: str | None = None

class MessageBrokerInfo(BaseModel):
    type: str; topics: list[str] = []

class IntegrationResult(BaseModel):
    external_apis: list[ExternalApiInfo] = []
    webhooks: list[str] = []
    third_party_services: list[ThirdPartyServiceInfo] = []
    message_brokers: list[MessageBrokerInfo] = []

class AuthResult(BaseModel):
    methods: list[str] = []
    authorization_pattern: str = ""
    identity_providers: list[str] = []
    token_management: str = ""
    permission_model: str = ""
    multi_tenant: bool = False

class ObservabilityResult(BaseModel):
    logging_framework: str = ""; log_format: str = ""
    metrics_tools: list[str] = []; tracing_tools: list[str] = []
    apm_tools: list[str] = []; error_tracking: list[str] = []
    health_checks: bool = False

class EndpointInfo(BaseModel):
    method: str; path: str; description: str | None = None

class ApiArchitectureResult(BaseModel):
    endpoints: list[EndpointInfo] = []
    api_style: str = ""; rate_limiting: bool = False
    versioning_strategy: str = ""; documentation_format: str = ""
    total_endpoints: int = 0

class DomainModelInfo(BaseModel):
    name: str; description: str | None = None

class WorkflowInfo(BaseModel):
    name: str; description: str | None = None; steps: list[str] = []

class BackgroundJobInfo(BaseModel):
    name: str; schedule: str | None = None; purpose: str | None = None

class BusinessLogicResult(BaseModel):
    domain_models: list[DomainModelInfo] = []
    workflows: list[WorkflowInfo] = []
    background_jobs: list[BackgroundJobInfo] = []
    state_machines: list[str] = []; event_patterns: list[str] = []

class InfrastructureResult(BaseModel):
    containerized: bool = False; orchestration: str = ""
    ci_cd_tools: list[str] = []; iac_tools: list[str] = []
    environments: list[str] = []; scaling_strategy: str = ""
    secrets_management: str = ""

class SecurityResult(BaseModel):
    encryption_at_rest: bool = False; encryption_in_transit: bool = False
    cors_configured: bool = False; input_validation: str = ""
    audit_logging: bool = False
    compliance_standards: list[str] = []; security_headers: list[str] = []

class FrontendResult(BaseModel):
    framework: str = ""; version: str = ""
    state_management: str = ""; routing_library: str = ""
    component_library: str = ""; build_tool: str = ""; has_ssr: bool = False

class ConfigurationResult(BaseModel):
    env_vars_count: int = 0; config_formats: list[str] = []
    feature_flags: str = ""; multi_env_strategy: str = ""
    secrets_approach: str = ""; dynamic_config: bool = False
```

### Aggregate

```python
class AnalysisResult(BaseModel):
    input_source: str
    input_type: str
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)

    tech_stack:       TechStackResult | None       = None
    dependencies:     DependencyResult | None      = None
    data_layer:       DataLayerResult | None       = None
    integrations:     IntegrationResult | None     = None
    auth:             AuthResult | None            = None
    observability:    ObservabilityResult | None   = None
    api_architecture: ApiArchitectureResult | None = None
    business_logic:   BusinessLogicResult | None   = None
    infrastructure:   InfrastructureResult | None  = None
    security:         SecurityResult | None        = None
    frontend:         FrontendResult | None        = None
    configuration:    ConfigurationResult | None   = None
```

---

## `agentfier.models.spec`

```python
class AgentDecomposition(BaseModel):
    name: str
    responsibilities: list[str] = []
    tools: list[str] = []

class MigrationPhase(BaseModel):
    phase: str                    # "1", "2", "3"…
    description: str | None = None
    tasks: list[str] = []
    risks: list[str] = []

class ConversionPlan(BaseModel):
    agent_decomposition: list[AgentDecomposition] = []
    communication_topology: str = ""
    orchestration_pattern: str = ""
    migration_phases: list[MigrationPhase] = []
    risk_assessment: str = ""

class AgentSpec(BaseModel):
    analysis: AnalysisResult
    conversion_plan: ConversionPlan | None = None
    diagram_paths: dict[str, str] = {}
    api_documentation: str | None = None
```

---

## `agentfier.claude.client`

```python
class ClaudeClient:
    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-6",
        max_tokens: int = 4096,
        temperature: float = 0.2,
    ) -> None: ...

    def analyze(
        self,
        system_prompt: str,
        user_content: str,
        result_model: type[T],   # Pydantic model class
        max_retries: int = 3,
    ) -> T:
        """Call Claude, strip JSON fences, validate against result_model.
        Retries up to max_retries on parse/validation errors, feeding the
        error back to Claude for self-correction."""

    def generate_diagram_spec(
        self,
        analysis_context: str,
        diagram_type: str,       # "c4_context" | "c4_container" | "c4_component"
    ) -> str:
        """Return Graphviz DOT source for the requested diagram type."""

    def generate_conversion_plan(
        self,
        analysis_summary: str,
    ) -> ConversionPlan:
        """Return a structured ConversionPlan for the analysed codebase."""

    def generate_flow_diagram(
        self,
        analysis_context: str,
    ) -> str:
        """Return Graphviz DOT source for a user-flow diagram."""
```

---

## `agentfier.ingestors`

```python
class BaseIngestor(ABC):
    def __init__(self, workspace_dir: str = "data/workspaces") -> None: ...

    @abstractmethod
    def ingest(self, source: Any) -> IngestResult: ...

    def _build_manifest(self, workspace_path: str) -> IngestResult:
        """Walk workspace_path, skip .git/node_modules/build/target,
        return IngestResult with file_manifest populated."""


class LocalIngestor(BaseIngestor):
    def ingest(self, path: str) -> IngestResult:
        """Validate path exists and is a directory, then call _build_manifest."""


class GitHubIngestor(BaseIngestor):
    def ingest(self, url: str) -> IngestResult:
        """Derive repo name from URL. If workspace exists, pull; else clone.
        Calls _build_manifest on the resulting directory."""


class JarIngestor(BaseIngestor):
    def ingest(self, source: str | bytes) -> IngestResult:
        """Accept a file path (str) or raw bytes.
        1. Extract ZIP to data/workspaces/{name}/extracted/
        2. Download CFR jar if tools/cfr.jar absent
        3. Decompile .class files → data/workspaces/{name}/decompiled/
        4. Call _build_manifest on decompiled directory."""
```

---

## `agentfier.analyzers`

```python
class BaseAnalyzer(ABC):
    DIMENSION: str            # unique dimension key, e.g. "tech_stack"
    PATTERNS: list[str]       # file glob patterns, e.g. ["**/*.py", "**/requirements.txt"]

    def __init__(self, claude: ClaudeClient) -> None: ...

    @abstractmethod
    def _heuristic(
        self,
        files: list[FileInfo],
        workspace: str,
    ) -> dict: ...
    """Pass 1: scan files locally, return structured findings dict."""

    def analyze(self, ingest_result: IngestResult) -> BaseModel:
        """Orchestrate Pass 1 + Pass 2 and return the Pydantic result model."""
```

Each concrete analyzer `analyze()` returns its dimension model:

| Analyzer class | Returns |
|----------------|---------|
| `TechStackAnalyzer` | `TechStackResult` |
| `DependencyAnalyzer` | `DependencyResult` |
| `DataLayerAnalyzer` | `DataLayerResult` |
| `IntegrationAnalyzer` | `IntegrationResult` |
| `AuthAnalyzer` | `AuthResult` |
| `ObservabilityAnalyzer` | `ObservabilityResult` |
| `ApiArchitectureAnalyzer` | `ApiArchitectureResult` |
| `BusinessLogicAnalyzer` | `BusinessLogicResult` |
| `InfrastructureAnalyzer` | `InfrastructureResult` |
| `SecurityAnalyzer` | `SecurityResult` |
| `FrontendAnalyzer` | `FrontendResult` |
| `ConfigurationAnalyzer` | `ConfigurationResult` |

---

## `agentfier.output`

```python
class SpecGenerator:
    def to_yaml(self, result: AnalysisResult) -> str: ...
    def to_json(self, result: AnalysisResult) -> str: ...
    def save(self, result: AnalysisResult, path: str | Path) -> None: ...
    def _dimension_section_name(self, key: str) -> str:
        """Maps Python field name → YAML section name.
        E.g. 'integrations' → 'integration_points',
             'auth' → 'authentication_authorization'."""


class ConversionPlanGenerator:
    def __init__(self, claude: ClaudeClient) -> None: ...
    def generate(self, result: AnalysisResult) -> ConversionPlan | None: ...
    def _build_summary(self, result: AnalysisResult) -> str: ...


class ApiDocGenerator:
    def generate(self, result: AnalysisResult) -> str | None:
        """Return Markdown API documentation or None if api_architecture is absent."""
```

---

## `agentfier.diagrams`

```python
class C4DiagramGenerator:
    def __init__(self, claude: ClaudeClient, output_dir: str) -> None: ...

    def generate_all(
        self, result: AnalysisResult
    ) -> dict[str, Path]:
        """Generate context, container, and component diagrams.
        Returns dict of level → file path (SVG, PNG, or DOT fallback)."""

    def generate(
        self,
        result: AnalysisResult,
        diagram_type: str,   # "c4_context" | "c4_container" | "c4_component"
    ) -> Path | None: ...

    def _build_analysis_context(self, result: AnalysisResult) -> str: ...
    def _render(self, dot_source: str, name: str) -> Path: ...


class FlowDiagramGenerator:
    def __init__(self, claude: ClaudeClient, output_dir: str) -> None: ...
    def generate(self, result: AnalysisResult) -> Path | None: ...
    def _build_analysis_context(self, result: AnalysisResult) -> str: ...
```
