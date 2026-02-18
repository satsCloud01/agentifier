# Agentfier - Codebase Analyzer Module

Agentfier analyzes existing codebases and deployment artifacts to produce a comprehensive architectural specification, then generates a detailed plan for converting the system to an **agent-native architecture**.

## What It Does

Given a codebase (via GitHub URL, JAR/WAR file, or local directory path), Agentfier:

1. **Ingests** the source - clones repos, decompiles JARs, or reads local directories
2. **Analyzes** the application across **12 architectural dimensions** using a combination of static heuristics and Claude AI
3. **Generates** a structured YAML/JSON specification of the entire system
4. **Produces** C4 architecture diagrams (Context, Container, Component levels)
5. **Creates** an agent-native conversion plan with migration roadmap

---

## Analysis Dimensions

| # | Dimension | What It Detects |
|---|-----------|----------------|
| 1 | **Technology Stack** | Languages, frameworks, build tools, runtime targets |
| 2 | **Dependencies** | Direct/transitive deps, licenses, vulnerabilities |
| 3 | **Data Layer** | Databases, ORMs, caches, message queues, migrations |
| 4 | **Integration Points** | External APIs, webhooks, third-party services, brokers |
| 5 | **Auth & Authorization** | JWT/OAuth/sessions, RBAC/ABAC, identity providers |
| 6 | **Observability** | Logging, metrics, tracing, APM, error tracking |
| 7 | **API Architecture** | Endpoints, REST/GraphQL/gRPC, rate limiting, versioning |
| 8 | **Business Logic** | Domain models, workflows, background jobs, state machines |
| 9 | **Infrastructure** | Docker, Kubernetes, CI/CD, IaC, scaling strategies |
| 10 | **Security** | Encryption, CORS, input validation, compliance |
| 11 | **Frontend** | React/Vue/Angular, state management, SSR, build tools |
| 12 | **Configuration** | Env vars, feature flags, multi-env strategy, secrets |

---

## Prerequisites

### Required

- **Python 3.10+**
- **Anthropic API Key** - for Claude-powered analysis

### Optional (for full functionality)

- **Java 17+** - required for JAR/WAR decompilation via CFR
- **Graphviz** - required for rendering C4 architecture diagrams

```bash
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz

# Windows
choco install graphviz
```

---

## Installation

### 1. Clone / navigate to the project

```bash
cd agentfier
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows
```

### 3. Install dependencies

```bash
pip install -e .
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set your Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-...
```

### 5. (Optional) Download CFR decompiler for JAR/WAR analysis

```bash
python scripts/download_cfr.py
```

This downloads the CFR decompiler to `tools/cfr.jar`. It will also auto-download on first use if not present.

---

## Usage

### Launch the UI

```bash
streamlit run src/agentfier/app.py
```

The application opens at `http://localhost:8501`.

### Input Sources

**GitHub Repository:**
Enter a public GitHub URL (e.g., `https://github.com/spring-projects/spring-petclinic`). The repo is shallow-cloned into `data/workspaces/`.

**JAR/WAR File:**
Upload a Java deployment artifact. Agentfier will:
- Extract the archive (MANIFEST.MF, pom.xml, web.xml, application.properties)
- Decompile `.class` files using CFR for deep source analysis
- Analyze both metadata and decompiled source code

**Local Directory:**
Enter an absolute path to a local project directory (e.g., `/Users/you/projects/my-app`).

### Workflow

1. **Analyze Page** - Select input source, choose dimensions, click "Start Analysis"
2. **Results Page** - Browse results across 12 tabbed dimensions, download YAML/JSON spec
3. **Diagrams Page** - Generate and view C4 architecture diagrams (Context, Container, Component)
4. **Conversion Plan Page** - Generate agent-native conversion strategy with migration roadmap

---

## Output Specification Format

The analysis produces a structured YAML/JSON specification:

```yaml
application:
  metadata:
    generated_by: "Agentfier Analyzer v0.1.0"
    generated_at: "2025-02-13T10:30:00"
    input_source: "https://github.com/user/repo"
    input_type: "github"

  technology_stack:
    languages:
      - name: "Java"
        version: "17"
        percentage: 75.0
      - name: "TypeScript"
        version: "5.3"
        percentage: 20.0
    frameworks:
      - name: "Spring Boot"
        version: "3.2.1"
        category: "Web Framework"
    build_tools: ["Maven", "npm"]
    runtime_targets: ["JVM 17", "Node.js 20"]

  dependencies:
    direct:
      - name: "spring-boot-starter-web"
        version: "3.2.1"
        purpose: "Web framework"
        license: "Apache-2.0"
    transitive_count: 142
    vulnerabilities:
      - package: "log4j-core"
        severity: "critical"
        description: "Remote code execution vulnerability"

  data_layer:
    databases:
      - type: "PostgreSQL"
        name: "primary"
        version: "15"
        purpose: "Main application data"
    orms: ["Spring Data JPA", "Hibernate"]
    cache_layers:
      - type: "Redis"
        purpose: "Session cache and rate limiting"
    message_queues:
      - type: "Kafka"
        purpose: "Event streaming"

  integration_points:
    external_apis:
      - name: "Stripe API"
        protocol: "REST"
        purpose: "Payment processing"
        auth_method: "API Key"
    third_party_services:
      - name: "SendGrid"
        category: "Email"
    message_brokers:
      - type: "Kafka"
        topics: ["orders", "notifications"]

  authentication_authorization:
    methods: ["JWT", "OAuth2"]
    authorization_pattern: "RBAC"
    identity_providers: ["Auth0"]
    token_management: "JWT with refresh tokens"
    permission_model: "Role-based with scopes"
    multi_tenant: true

  # ... additional dimensions ...
```

---

## Architecture Diagrams

Agentfier generates **C4 model** architecture diagrams at three levels:

### Level 1: System Context
Shows the system under analysis, its users, and external systems it interacts with.

### Level 2: Container
Shows the high-level technical building blocks (web app, API server, database, cache, message queue, workers).

### Level 3: Component
Shows the major components within each container (controllers, services, repositories, etc.).

### User Flow Diagrams
Visualizes the main user journeys through the system based on API endpoints and business logic.

Diagrams are generated using Claude AI (produces Graphviz DOT code) and rendered as SVG/PNG via the Graphviz engine.

---

## Agent-Native Conversion Plan

The conversion plan transforms your traditional architecture into an agent-native system:

```yaml
conversion_plan:
  agent_decomposition:
    - name: "Data Agent"
      responsibilities:
        - "Database queries and data retrieval"
        - "Cache management"
        - "Data validation and transformation"
      tools:
        - "sql_query"
        - "cache_get"
        - "cache_set"

    - name: "API Gateway Agent"
      responsibilities:
        - "Request routing and authentication"
        - "Rate limiting and throttling"
        - "Response formatting"
      tools:
        - "validate_token"
        - "route_request"
        - "apply_rate_limit"

    - name: "Business Logic Agent"
      responsibilities:
        - "Order processing workflows"
        - "Business rule validation"
        - "State machine transitions"
      tools:
        - "process_order"
        - "validate_rules"
        - "transition_state"

  communication_topology: "Hub-and-spoke with message bus"
  orchestration_pattern: "Supervisor agent with specialized workers"

  migration_phases:
    - phase: 1
      name: "Foundation"
      description: "Set up agent framework and communication infrastructure"
      tasks:
        - "Deploy message bus (NATS/Kafka)"
        - "Create agent base classes and tool registry"
        - "Set up agent observability"
      risks:
        - "Message ordering guarantees"

    - phase: 2
      name: "Data Layer Migration"
      description: "Convert data access to agent-mediated operations"
      tasks:
        - "Wrap database operations as agent tools"
        - "Implement caching agent"
      risks:
        - "Transaction consistency across agents"
```

---

## Configuration

All configuration is via environment variables (`.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | (required) | Your Anthropic API key |
| `CLAUDE_MODEL` | `claude-sonnet-4-5-20250929` | Claude model to use |
| `MAX_TOKENS` | `4096` | Max tokens per Claude response |
| `TEMPERATURE` | `0.2` | Temperature for analysis (lower = more factual) |
| `CFR_JAR_PATH` | `tools/cfr.jar` | Path to CFR decompiler |
| `WORKSPACE_DIR` | `data/workspaces` | Where cloned repos/extracted JARs are stored |
| `OUTPUT_DIR` | `data/outputs` | Where specs and diagrams are saved |
| `MAX_FILE_SIZE_MB` | `100` | Max file size to process |
| `MAX_FILES_TO_ANALYZE` | `500` | Safety cap on files per analyzer |

---

## Project Structure

```
agentfier/
├── src/agentfier/
│   ├── app.py                    # Streamlit entry point
│   ├── config.py                 # Pydantic configuration
│   ├── models/
│   │   ├── enums.py              # InputType, AnalysisStatus, DiagramLevel
│   │   ├── analysis.py           # Pydantic models for all 12 dimensions
│   │   └── spec.py               # AgentSpec + ConversionPlan models
│   ├── ingestors/
│   │   ├── base.py               # BaseIngestor ABC
│   │   ├── github_ingestor.py    # Git clone via gitpython
│   │   ├── jar_ingestor.py       # JAR/WAR extraction + CFR decompilation
│   │   └── local_ingestor.py     # Local directory analysis
│   ├── analyzers/
│   │   ├── base.py               # BaseAnalyzer ABC (heuristic + Claude pattern)
│   │   ├── tech_stack.py         # Technology Stack & Runtime
│   │   ├── dependencies.py       # Dependency Analysis
│   │   ├── data_layer.py         # Data Layer
│   │   ├── integrations.py       # Integration Points
│   │   ├── auth.py               # Authentication & Authorization
│   │   ├── observability.py      # Observability & Monitoring
│   │   ├── api_architecture.py   # API Architecture
│   │   ├── business_logic.py     # Business Logic & Workflows
│   │   ├── infrastructure.py     # Infrastructure & Deployment
│   │   ├── security.py           # Security & Compliance
│   │   ├── frontend.py           # Frontend Architecture
│   │   └── configuration.py      # Configuration Management
│   ├── claude/
│   │   ├── client.py             # Anthropic SDK wrapper with retry logic
│   │   └── prompts.py            # Prompt templates for all 12 dimensions
│   ├── diagrams/
│   │   ├── c4_generator.py       # C4 diagram generation (Context/Container/Component)
│   │   └── flow_generator.py     # User flow diagram generation
│   ├── output/
│   │   ├── spec_generator.py     # YAML/JSON specification assembler
│   │   ├── conversion_plan.py    # Agent-native conversion plan generator
│   │   └── api_doc_generator.py  # API documentation generator
│   └── ui/
│       └── pages/
│           ├── analyze.py        # Input + analysis execution page
│           ├── results.py        # 12-tab results viewer
│           ├── diagrams.py       # C4 + flow diagram viewer
│           └── conversion.py     # Conversion plan viewer
├── scripts/
│   └── download_cfr.py           # CFR decompiler auto-download
├── tools/                        # CFR jar (auto-downloaded)
├── data/
│   ├── workspaces/               # Cloned repos, extracted JARs
│   └── outputs/                  # Generated specs, diagrams
├── pyproject.toml
├── .env.example
└── .gitignore
```

---

## How It Works

### Analysis Methodology

Each analyzer follows a two-pass approach:

**Pass 1 - Heuristic Analysis (local, fast):**
- Glob-match relevant files (e.g., `**/models/**/*.py`, `**/Dockerfile*`)
- Pattern-match imports, decorators, and configurations
- Count file types, detect frameworks by convention
- Build a structured findings dictionary

**Pass 2 - Claude AI Analysis (enrichment):**
- Send heuristic findings + relevant file contents to Claude
- Claude confirms, corrects, and enriches the findings
- Response is validated against a Pydantic schema
- Retry with error correction on parse failure

This hybrid approach keeps API costs low while ensuring high-quality analysis.

### Token Usage

Each analysis dimension uses approximately 10,000-18,000 tokens. A full 12-dimension analysis plus diagram generation and conversion plan uses approximately **200,000-250,000 tokens** total.

---

## Supported Technologies

### Languages
Python, Java, JavaScript, TypeScript, Go, Rust, Ruby, C#, Kotlin, Scala, PHP, Swift, C/C++, Dart

### Frameworks
Spring Boot, Django, Flask, FastAPI, Express, Next.js, React, Vue, Angular, Svelte, Rails, .NET, Gin, Echo

### Build Tools
Maven, Gradle, npm, yarn, pip, Poetry, Cargo, Go modules, Bundler, Composer

### Databases
PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch, SQLite, DynamoDB, Cassandra

### Infrastructure
Docker, Kubernetes, Terraform, CloudFormation, GitHub Actions, Jenkins, CircleCI, Helm

---

## Development

### Install dev dependencies

```bash
pip install -e ".[dev]"
```

### Run linting

```bash
ruff check src/
```

### Run tests

```bash
pytest
```

---

## Limitations

- **Private repositories** require appropriate Git credentials configured on the machine
- **Obfuscated JARs** may produce partial decompilation results
- **Very large codebases** (10K+ files) are capped at `MAX_FILES_TO_ANALYZE` per dimension
- **Binary files** and `node_modules`/`.git`/`target`/`build` directories are automatically skipped
- **Claude API rate limits** may slow analysis for rapid consecutive runs
- **Graphviz system package** must be installed separately for diagram rendering

---

## License

MIT
