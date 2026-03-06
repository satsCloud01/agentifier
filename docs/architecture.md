# Agentfier — Architecture Documentation

> C1 System Context · C2 Container · C3 Component · C4 Code

---

## C1 — System Context

Agentfier is a web-based analysis tool that accepts a codebase (GitHub URL, local path, or JAR/WAR) and produces a structured architectural specification plus an agent-native conversion plan.

```
┌─────────────────────────────────────────────────────────────────────┐
│                          System Boundary                            │
│                                                                     │
│   ┌───────────┐           ┌──────────────────────┐                  │
│   │  Developer│  browser  │                      │                  │
│   │  / Analyst│ ────────► │      Agentfier       │                  │
│   └───────────┘           │  (Streamlit Web App) │                  │
│                           └──────────┬───────────┘                  │
│                                      │                              │
└──────────────────────────────────────│──────────────────────────────┘
                                       │
              ┌──────────────┬─────────┼─────────────────┐
              ▼              ▼         ▼                  ▼
      ┌──────────────┐ ┌──────────┐ ┌───────────┐ ┌────────────┐
      │  Anthropic   │ │  GitHub  │ │  Local FS │ │  Maven /   │
      │  Claude API  │ │  (git)   │ │ (codebase)│ │  JAR / WAR │
      └──────────────┘ └──────────┘ └───────────┘ └────────────┘
```

**External actors:**

| Actor | Role |
|-------|------|
| Developer / Analyst | Browses the Streamlit UI, provides input, views results |
| Anthropic Claude API | Powers AI-enrichment pass for each analysis dimension |
| GitHub | Source of truth for GitHub-URL ingestion (shallow clone) |
| Local Filesystem | Source for local-directory ingestion and output storage |
| JAR / WAR archive | Compiled Java artifact for JAR-mode ingestion |

---

## C2 — Container View

```
┌────────────────────────────────────────────────────────────────────────┐
│                          Agentfier Process                             │
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  Streamlit UI Layer                                             │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────┐ │  │
│  │  │  Tour    │ │ Analyze  │ │ Results  │ │ Diagrams │ │Conv. │ │  │
│  │  │  (guide) │ │  Page   │ │   Page   │ │  Page    │ │Plan  │ │  │
│  │  └──────────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └──┬───┘ │  │
│  └───────────────────────────────────────────────────────────────  │  │
│                        │ st.session_state                           │  │
│  ┌─────────────────────▼───────────────────────────────────────┐  │  │
│  │  Core Engine                                                │  │  │
│  │                                                             │  │  │
│  │  ┌────────────┐  ┌─────────────┐  ┌────────────────────┐  │  │  │
│  │  │  Ingestors │  │  Analyzers  │  │  Output Generators │  │  │  │
│  │  │            │  │  (×12 dims) │  │                    │  │  │  │
│  │  │ - GitHub   │  │  BaseAnalyz.│  │ - SpecGenerator    │  │  │  │
│  │  │ - Local    │  │  + 12 impls │  │ - ConversionPlan   │  │  │  │
│  │  │ - JAR/WAR  │  └──────┬──────┘  │ - ApiDocGenerator  │  │  │  │
│  │  └─────┬──────┘         │         └────────────────────┘  │  │  │
│  │        │         ┌──────▼──────┐                          │  │  │
│  │        │         │ ClaudeClient│ ◄──── Anthropic API      │  │  │
│  │        │         └─────────────┘                          │  │  │
│  │        │                                                   │  │  │
│  │  ┌─────▼────────────────────────────────────────────────┐  │  │  │
│  │  │  Diagrams                                            │  │  │  │
│  │  │  C4DiagramGenerator · FlowDiagramGenerator           │  │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │  │
│  └─────────────────────────────────────────────────────────────┘  │  │
│                                                                        │
│  ┌────────────────────────────────────┐                              │
│  │  Local Filesystem                  │                              │
│  │  data/workspaces/   data/outputs/  │                              │
│  └────────────────────────────────────┘                              │
└────────────────────────────────────────────────────────────────────────┘
```

**Containers:**

| Container | Technology | Responsibility |
|-----------|------------|----------------|
| Streamlit UI | Python · Streamlit 1.40+ | All user interaction; session state management |
| Ingestors | Python · GitPython · zipfile · subprocess | Source code acquisition and workspace setup |
| Analyzers | Python · BaseAnalyzer ABC | 12-dimension heuristic + Claude two-pass analysis |
| ClaudeClient | Python · Anthropic SDK | API calls with retry, JSON parsing, error correction |
| Output Generators | Python · PyYAML · Pydantic | YAML/JSON spec, conversion plan, API docs |
| Diagram Generators | Python · Graphviz | C4 DOT-code generation + rendering |
| Local Filesystem | OS filesystem | Workspace clones, output files, CFR jar |

---

## C3 — Component View

### Ingestors (`src/agentfier/ingestors/`)

```
BaseIngestor (ABC)
│   ingest(source) → IngestResult
│   _build_manifest(path) → IngestResult
│
├── LocalIngestor
│   └── ingest(path: str) → IngestResult
│       Validates path exists, calls _build_manifest
│
├── GitHubIngestor
│   └── ingest(url: str) → IngestResult
│       Derives repo name from URL, shallow-clones or pulls into
│       data/workspaces/{repo_name}, calls _build_manifest
│
└── JarIngestor
    └── ingest(source: str | bytes) → IngestResult
        Extracts ZIP into data/workspaces/{name}/extracted/
        Downloads CFR jar if absent, decompiles .class files into
        data/workspaces/{name}/decompiled/, calls _build_manifest
```

### Analyzers (`src/agentfier/analyzers/`)

```
BaseAnalyzer (ABC)
│   DIMENSION: str          # e.g. "tech_stack"
│   PATTERNS: list[str]     # file glob patterns to match
│   analyze(ingest_result) → Pydantic model
│   _heuristic(files, workspace) → dict
│   _call_claude(heuristic_findings, file_contents) → Pydantic model
│
├── TechStackAnalyzer        → TechStackResult
├── DependencyAnalyzer       → DependencyResult
├── DataLayerAnalyzer        → DataLayerResult
├── IntegrationAnalyzer      → IntegrationResult
├── AuthAnalyzer             → AuthResult
├── ObservabilityAnalyzer    → ObservabilityResult
├── ApiArchitectureAnalyzer  → ApiArchitectureResult
├── BusinessLogicAnalyzer    → BusinessLogicResult
├── InfrastructureAnalyzer   → InfrastructureResult
├── SecurityAnalyzer         → SecurityResult
├── FrontendAnalyzer         → FrontendResult
└── ConfigurationAnalyzer    → ConfigurationResult
```

### ClaudeClient (`src/agentfier/claude/`)

```
ClaudeClient
│   __init__(api_key, model, max_tokens, temperature)
│
│   analyze(system_prompt, user_content, result_model) → Pydantic model
│   │   POST /messages · retry up to 3× on JSON/parse errors
│   │   Strips markdown fences · validates against result_model
│
│   generate_diagram_spec(analysis_context, diagram_type) → str
│   │   Returns Graphviz DOT source
│
│   generate_conversion_plan(analysis_summary) → ConversionPlan
│   │   Returns structured ConversionPlan Pydantic model
│
│   generate_flow_diagram(analysis_context) → str
│       Returns Graphviz DOT source for user-flow diagram
```

### Output Generators (`src/agentfier/output/`)

```
SpecGenerator
│   to_yaml(analysis_result) → str
│   to_json(analysis_result) → str
│   save(analysis_result, path)
│   _dimension_section_name(key) → str   # maps field name → YAML key

ConversionPlanGenerator
│   generate(analysis_result) → ConversionPlan | None
│   _build_summary(analysis_result) → str

ApiDocGenerator
    generate(analysis_result) → str | None
    Produces Markdown API documentation from api_architecture dimension
```

### Diagram Generators (`src/agentfier/diagrams/`)

```
C4DiagramGenerator
│   __init__(claude_client, output_dir)
│   generate_all(analysis_result) → dict[str, Path]
│       Calls generate(analysis, "c4_context"), "c4_container", "c4_component"
│   generate(analysis_result, diagram_type) → Path | None
│   _render(dot_source, name) → Path   # graphviz.Source.render()
│   _build_analysis_context(analysis_result) → str

FlowDiagramGenerator
    __init__(claude_client, output_dir)
    generate(analysis_result) → Path | None
    _build_analysis_context(analysis_result) → str
```

### UI Pages (`src/agentfier/ui/pages/`)

```
guide.py    → Interactive 7-step wizard with Spring PetClinic demo
analyze.py  → Input form + analysis orchestration + progress tracking
results.py  → 12-tab result viewer + YAML/JSON download
diagrams.py → C4 + flow diagram generation + image/DOT display
conversion.py → ConversionPlan display + API doc + YAML download
```

---

## C4 — Code / Key Patterns

### Two-Pass Analysis Pattern

```python
class BaseAnalyzer(ABC):
    @abstractmethod
    def _heuristic(self, files: list[FileInfo], workspace: str) -> dict:
        """Pass 1: fast local scan, returns structured findings."""

    def analyze(self, ingest_result: IngestResult) -> BaseModel:
        # Pass 1
        findings = self._heuristic(ingest_result.file_manifest,
                                   ingest_result.workspace_path)
        # Pass 2: Claude enrichment
        relevant_files = self._sample_relevant_files(ingest_result)
        result = self._call_claude(findings, relevant_files)
        return result
```

### Retry / Parse Correction Pattern

```python
def analyze(self, system_prompt, user_content, result_model):
    for attempt in range(3):
        response = self._client.messages.create(...)
        raw = response.content[0].text
        raw = self._strip_fences(raw)   # remove ```json ... ```
        try:
            return result_model.model_validate_json(raw)
        except (ValidationError, JSONDecodeError) as e:
            if attempt == 2:
                raise
            user_content += f"\n\nError on attempt {attempt+1}: {e}\nPlease fix."
```

### Session-State API Key Flow

```python
# app.py — sidebar (always visible, never reads from env)
api_key = st.text_input("API Key", type="password",
                        value=st.session_state.get("api_key", ""),
                        placeholder="sk-ant-… (session only)")
if api_key:
    st.session_state.api_key = api_key
elif "api_key" in st.session_state and not api_key:
    del st.session_state.api_key   # user cleared the field

# In every page that calls Claude:
api_key = st.session_state.get("api_key", "")   # NO os.environ fallback
if not api_key:
    st.warning("Enter API key in sidebar")
    return
```

---

## Data Flow

```
User Input (URL / path / JAR)
        │
        ▼
  Ingestor.ingest()
        │  IngestResult (workspace_path, file_manifest)
        ▼
  [For each selected dimension]
  Analyzer._heuristic()          ← local, fast, free
        │  findings: dict
        ▼
  ClaudeClient.analyze()         ← Anthropic API
        │  Pydantic dimension model
        ▼
  AnalysisResult aggregate
        │
        ├──► SpecGenerator.to_yaml/json()  → download
        │
        ├──► C4DiagramGenerator.generate_all()
        │       ClaudeClient.generate_diagram_spec() → DOT → SVG/PNG
        │
        └──► ConversionPlanGenerator.generate()
                ClaudeClient.generate_conversion_plan() → ConversionPlan
```

---

## Domain Model

See [domain-model.md](domain-model.md) for the full entity relationship diagram.

## API Specification

See [api-spec.md](api-spec.md) for Python module API signatures.

## Constraints

See [constraints.md](constraints.md) for technical and design constraints.
