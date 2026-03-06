"""
Agentfier — Interactive Tour / Wizard Page

A step-by-step guide through all capabilities, with a live demo
that loads example analysis data so users can explore the full UI
without needing an API key.
"""

import streamlit as st

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
    FrontendResult,
    FrameworkInfo,
    InfrastructureResult,
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
from agentfier.models.spec import AgentDecomposition, ConversionPlan, MigrationPhase


# ── Constants ─────────────────────────────────────────────────────────────────

TOTAL_STEPS = 7

STEP_LABELS = [
    "Welcome",
    "Input Sources",
    "Analysis Dimensions",
    "How Analysis Works",
    "Live Demo — Results",
    "Architecture Diagrams",
    "Agent Conversion Plan",
]

STEP_ICONS = ["⬡", "📂", "🔬", "⚙", "📊", "🗺", "🤖"]


# ── Sample data (Spring PetClinic-inspired demo) ──────────────────────────────

def _build_example_analysis() -> AnalysisResult:
    return AnalysisResult(
        input_source="https://github.com/spring-projects/spring-petclinic",
        input_type="github",
        tech_stack=TechStackResult(
            languages=[
                LanguageInfo(name="Java", version="17", percentage=82.0),
                LanguageInfo(name="HTML/Thymeleaf", percentage=10.0),
                LanguageInfo(name="CSS", percentage=5.0),
                LanguageInfo(name="JavaScript", percentage=3.0),
            ],
            frameworks=[
                FrameworkInfo(name="Spring Boot", version="3.2.1", category="Web Framework"),
                FrameworkInfo(name="Spring Data JPA", version="3.2.1", category="ORM"),
                FrameworkInfo(name="Thymeleaf", version="3.1.2", category="Template Engine"),
                FrameworkInfo(name="Spring Security", version="3.2.1", category="Security"),
            ],
            build_tools=["Maven 3.9"],
            runtime_targets=["JVM 17", "Embedded Tomcat 10"],
            confidence=0.97,
        ),
        dependencies=DependencyResult(
            direct=[
                DependencyInfo(name="spring-boot-starter-web", version="3.2.1", purpose="Web MVC framework", license="Apache-2.0"),
                DependencyInfo(name="spring-boot-starter-data-jpa", version="3.2.1", purpose="JPA / Hibernate ORM", license="Apache-2.0"),
                DependencyInfo(name="spring-boot-starter-security", version="3.2.1", purpose="Authentication & authorization", license="Apache-2.0"),
                DependencyInfo(name="h2", version="2.2.224", purpose="In-memory database (dev/test)", license="EPL-1.0"),
                DependencyInfo(name="mysql-connector-j", version="8.2.0", purpose="MySQL JDBC driver (prod)", license="GPL-2.0"),
                DependencyInfo(name="spring-boot-starter-thymeleaf", version="3.2.1", purpose="Server-side templating", license="Apache-2.0"),
                DependencyInfo(name="spring-boot-starter-validation", version="3.2.1", purpose="Bean validation (JSR-380)", license="Apache-2.0"),
                DependencyInfo(name="spring-boot-starter-actuator", version="3.2.1", purpose="Health checks & metrics", license="Apache-2.0"),
            ],
            transitive_count=87,
            licenses={"Apache-2.0": ["spring-*", "jackson-*"], "EPL-1.0": ["h2"], "GPL-2.0": ["mysql-connector-j"]},
            vulnerabilities=[
                VulnerabilityInfo(package="spring-webmvc", severity="medium", description="Reflected XSS via error message (patched in 3.2.2)"),
            ],
        ),
        data_layer=DataLayerResult(
            databases=[
                DatabaseInfo(type="MySQL", name="petclinic", version="8.0", purpose="Production data store"),
                DatabaseInfo(type="H2", name="testdb", purpose="In-memory dev/test database"),
            ],
            orms=["Spring Data JPA", "Hibernate 6.4"],
            cache_layers=[CacheLayerInfo(type="Caffeine", purpose="In-process L1 cache for vet specialties")],
            message_queues=[],
            has_migrations=True,
        ),
        integrations=IntegrationResult(
            external_apis=[
                ExternalApiInfo(name="Spring Boot Actuator", protocol="HTTP", purpose="Metrics & health exposition", auth_method="None (internal)"),
            ],
            webhooks=[],
            third_party_services=[
                ThirdPartyServiceInfo(name="Prometheus", category="Monitoring"),
                ThirdPartyServiceInfo(name="Grafana", category="Dashboarding"),
            ],
            message_brokers=[],
        ),
        auth=AuthResult(
            methods=["Form Login", "HTTP Basic"],
            authorization_pattern="Role-Based Access Control (RBAC)",
            identity_providers=["In-memory UserDetailsService"],
            token_management="HTTP Session (stateful)",
            permission_model="hasRole() annotations + URL matchers",
            multi_tenant=False,
        ),
        observability=ObservabilityResult(
            logging_framework="Logback (via SLF4J)",
            log_format="text (structured JSON in prod profile)",
            metrics_tools=["Micrometer", "Prometheus"],
            tracing_tools=["Spring Boot Actuator Tracing"],
            apm_tools=[],
            error_tracking=[],
            health_checks=True,
        ),
        api_architecture=ApiArchitectureResult(
            endpoints=[
                EndpointInfo(method="GET",  path="/",                     description="Welcome / home page"),
                EndpointInfo(method="GET",  path="/owners",               description="List owners with optional search"),
                EndpointInfo(method="GET",  path="/owners/{ownerId}",     description="Owner detail"),
                EndpointInfo(method="POST", path="/owners/new",           description="Create owner"),
                EndpointInfo(method="PUT",  path="/owners/{ownerId}/edit",description="Edit owner"),
                EndpointInfo(method="GET",  path="/owners/{ownerId}/pets/new", description="Add pet form"),
                EndpointInfo(method="POST", path="/owners/{ownerId}/pets/new", description="Create pet"),
                EndpointInfo(method="GET",  path="/vets.html",            description="Vets list (HTML + JSON)"),
                EndpointInfo(method="GET",  path="/actuator/health",      description="Health check"),
                EndpointInfo(method="GET",  path="/actuator/metrics",     description="Prometheus metrics"),
            ],
            api_style="MVC (Thymeleaf) + REST (Actuator)",
            rate_limiting=False,
            versioning_strategy="None (single version)",
            documentation_format="Spring REST Docs",
            total_endpoints=10,
        ),
        business_logic=BusinessLogicResult(
            domain_models=[
                DomainModelInfo(name="Owner",   description="Pet clinic client with contact details"),
                DomainModelInfo(name="Pet",     description="Animal owned by a client, has type & birthDate"),
                DomainModelInfo(name="Visit",   description="Vet appointment record linked to a Pet"),
                DomainModelInfo(name="Vet",     description="Veterinarian with specialties"),
                DomainModelInfo(name="Specialty", description="Medical specialty (e.g. surgery, dentistry)"),
            ],
            workflows=[
                WorkflowInfo(
                    name="Register Owner & Pet",
                    description="New client registration including pet assignment",
                    steps=["Submit owner form", "Validate bean constraints", "Persist Owner", "Redirect to pet creation", "Persist Pet linked to Owner"],
                ),
                WorkflowInfo(
                    name="Schedule Visit",
                    description="Book a vet appointment for a pet",
                    steps=["Navigate to pet detail", "Click 'Add Visit'", "Submit visit form with date/description", "Persist Visit", "Show confirmation"],
                ),
            ],
            background_jobs=[],
            state_machines=[],
            event_patterns=["Spring ApplicationEvent for cache refresh"],
        ),
        infrastructure=InfrastructureResult(
            containerized=True,
            orchestration="Docker Compose (dev) / Kubernetes (prod)",
            ci_cd_tools=["GitHub Actions"],
            iac_tools=[],
            environments=["local", "test", "production"],
            scaling_strategy="Horizontal Pod Autoscaling (HPA) on CPU",
            secrets_management="Kubernetes Secrets / env vars",
        ),
        security=SecurityResult(
            encryption_at_rest=False,
            encryption_in_transit=True,
            cors_configured=False,
            input_validation="Bean Validation (Jakarta EE 10) on all forms",
            audit_logging=False,
            compliance_standards=[],
            security_headers=["X-Content-Type-Options", "X-Frame-Options", "Cache-Control"],
        ),
        frontend=FrontendResult(
            framework="Thymeleaf",
            version="3.1.2",
            state_management="Server-side session",
            routing_library="Spring MVC",
            component_library="Bootstrap 5",
            build_tool="Webjars / Maven",
            has_ssr=True,
        ),
        configuration=ConfigurationResult(
            env_vars_count=12,
            config_formats=["application.properties", "application-prod.yml", "application-test.yml"],
            feature_flags="None",
            multi_env_strategy="Spring Profiles (local / test / prod)",
            secrets_approach="Environment variables injected at runtime",
            dynamic_config=False,
        ),
    )


def _build_example_plan() -> ConversionPlan:
    return ConversionPlan(
        agent_decomposition=[
            AgentDecomposition(
                name="Data Agent",
                responsibilities=[
                    "Execute JPA queries through a safe tool interface",
                    "Manage cache invalidation and refresh",
                    "Validate entity constraints before persistence",
                ],
                tools=["sql_query", "cache_get", "cache_set", "validate_entity"],
            ),
            AgentDecomposition(
                name="Domain Agent",
                responsibilities=[
                    "Enforce business rules (Owner → Pet → Visit lifecycle)",
                    "Coordinate multi-step workflows across domain models",
                    "Emit domain events for downstream agents",
                ],
                tools=["create_owner", "create_pet", "schedule_visit", "emit_event"],
            ),
            AgentDecomposition(
                name="Auth Agent",
                responsibilities=[
                    "Verify user credentials and issue session tokens",
                    "Enforce role-based permissions on operations",
                    "Audit sensitive actions",
                ],
                tools=["verify_credentials", "check_role", "issue_token", "audit_log"],
            ),
            AgentDecomposition(
                name="Presentation Agent",
                responsibilities=[
                    "Render Thymeleaf templates with agent-provided data",
                    "Route HTTP requests to appropriate domain agents",
                    "Handle validation error display",
                ],
                tools=["render_template", "route_request", "format_errors"],
            ),
            AgentDecomposition(
                name="Observability Agent",
                responsibilities=[
                    "Collect metrics from all agents via Micrometer",
                    "Forward traces to distributed tracing backend",
                    "Alert on SLA violations",
                ],
                tools=["record_metric", "emit_trace", "fire_alert"],
            ),
        ],
        communication_topology="Hub-and-spoke: Orchestrator → Domain/Data/Auth Agents",
        orchestration_pattern="Supervisor agent (Orchestrator) with specialist worker agents",
        migration_phases=[
            MigrationPhase(
                phase="1",
                description="Establish agent framework and communication infrastructure",
                tasks=[
                    "Choose agent framework (Claude Agent SDK / LangGraph)",
                    "Define tool schemas for each agent",
                    "Set up inter-agent message bus (NATS or in-process)",
                    "Create shared observability pipeline",
                ],
                risks=["Framework lock-in", "Latency overhead vs direct method calls"],
            ),
            MigrationPhase(
                phase="2",
                description="Migrate data access layer to agent-mediated operations",
                tasks=[
                    "Wrap all JPA repositories as Data Agent tools",
                    "Implement Caffeine cache as Data Agent managed resource",
                    "Add retry / circuit-breaker to Data Agent tools",
                    "Validate functional parity with integration tests",
                ],
                risks=["Transaction boundary changes", "N+1 query patterns through tool calls"],
            ),
            MigrationPhase(
                phase="3",
                description="Extract business logic into Domain Agent",
                tasks=[
                    "Model Owner/Pet/Visit workflows as agent-driven sequences",
                    "Replace Spring ApplicationEvents with agent-to-agent messages",
                    "Implement Domain Agent with full workflow coverage",
                ],
                risks=["Distributed transaction consistency", "Workflow state persistence"],
            ),
            MigrationPhase(
                phase="4",
                description="Harden, observe, and go live",
                tasks=[
                    "Enable full observability across all agents",
                    "Load-test multi-agent system",
                    "Gradual traffic cut-over with feature flags",
                    "Monitor for regressions; rollback plan in place",
                ],
                risks=["Latency increase under load", "Debugging complexity of agent chains"],
            ),
        ],
        risk_assessment=(
            "Medium-risk migration. The existing monolith is well-structured (clear domain boundaries, "
            "thin controllers), which simplifies agent decomposition. Primary risks are distributed "
            "transaction consistency during Phase 2-3 and per-call latency increase (~5-15ms) introduced "
            "by agent mediation. Recommend a parallel-run strategy with feature-flag gating for each phase."
        ),
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _step_indicator(current: int) -> None:
    dots = ""
    for i in range(TOTAL_STEPS):
        if i == current:
            dots += f'<span style="display:inline-block;width:22px;height:22px;border-radius:50%;background:#6366f1;color:#fff;font-size:0.68rem;font-weight:700;line-height:22px;text-align:center;margin:0 3px;">{i+1}</span>'
        elif i < current:
            dots += f'<span style="display:inline-block;width:22px;height:22px;border-radius:50%;background:#1e293b;color:#34d399;font-size:0.7rem;line-height:22px;text-align:center;margin:0 3px;border:1px solid #34d399;">✓</span>'
        else:
            dots += f'<span style="display:inline-block;width:22px;height:22px;border-radius:50%;background:#0f172a;color:#334155;font-size:0.68rem;font-weight:700;line-height:22px;text-align:center;margin:0 3px;border:1px solid #1e293b;">{i+1}</span>'
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:0;margin-bottom:20px;">'
        f'{dots}'
        f'<span style="color:#475569;font-size:0.78rem;margin-left:12px;">'
        f'Step {current+1} of {TOTAL_STEPS} — {STEP_LABELS[current]}</span></div>',
        unsafe_allow_html=True,
    )


def _nav_buttons(step: int) -> None:
    col_back, col_space, col_next = st.columns([1, 5, 1])
    with col_back:
        if step > 0:
            if st.button("← Back", key="guide_back", use_container_width=True):
                st.session_state.guide_step = step - 1
                st.rerun()
    with col_next:
        if step < TOTAL_STEPS - 1:
            if st.button("Next →", key="guide_next", type="primary", use_container_width=True):
                st.session_state.guide_step = step + 1
                st.rerun()
        else:
            if st.button("✓ Done", key="guide_done", type="primary", use_container_width=True):
                st.session_state.guide_step = 0
                st.rerun()


def _card(content: str, border: str = "#1e293b") -> None:
    st.markdown(
        f'<div class="ag-card" style="border-left:3px solid {border};">{content}</div>',
        unsafe_allow_html=True,
    )


def _badge(label: str, variant: str = "") -> str:
    cls = f"ag-badge {f'ag-badge-{variant}' if variant else ''}"
    return f'<span class="{cls}">{label}</span>'


# ── Step renderers ────────────────────────────────────────────────────────────

def _step_welcome() -> None:
    st.markdown(
        """
<div class="ag-card" style="text-align:center;padding:36px 24px;border-top:3px solid #6366f1;">
  <div style="font-size:2.5rem;margin-bottom:12px;">⬡</div>
  <div style="font-size:1.4rem;font-weight:700;color:#f1f5f9;margin-bottom:8px;">
    Welcome to Agentfier
  </div>
  <div style="color:#64748b;font-size:0.9rem;max-width:520px;margin:0 auto;line-height:1.6;">
    Agentfier analyzes your existing codebase across <strong style="color:#818cf8">12 architectural dimensions</strong>
    and generates a detailed plan to transform it into an <strong style="color:#818cf8">agent-native architecture</strong>
    powered by Claude AI.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown("")

    cols = st.columns(4)
    features = [
        ("📂", "Ingest",      "GitHub, local directory, or Java JAR/WAR"),
        ("🔬", "Analyze",     "12 dimensions: stack, data, API, security, and more"),
        ("🗺", "Visualize",   "C4 architecture diagrams (Context → Component)"),
        ("🤖", "Convert",     "Agent decomposition + phased migration roadmap"),
    ]
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            st.markdown(
                f'<div class="ag-card" style="text-align:center;padding:18px 12px;">'
                f'<div style="font-size:1.6rem;margin-bottom:8px;">{icon}</div>'
                f'<div style="font-weight:700;color:#f1f5f9;margin-bottom:4px;">{title}</div>'
                f'<div style="color:#475569;font-size:0.78rem;">{desc}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("")
    st.markdown(
        '<div class="ag-card" style="border-left:3px solid #6366f1;padding:14px 18px;">'
        '<strong style="color:#818cf8">👋 This guided tour</strong>'
        '<div style="color:#64748b;font-size:0.85rem;margin-top:6px;">'
        'Walk through all 7 steps to understand every feature. '
        'On <strong style="color:#e2e8f0">Step 5</strong> you can load a live demo '
        '(Spring PetClinic analysis) without needing an API key — then explore '
        'the Results, Diagrams, and Conversion Plan pages yourself.</div></div>',
        unsafe_allow_html=True,
    )


def _step_input_sources() -> None:
    st.markdown(
        '<div class="ag-page-title"><span class="ag-icon">📂</span> Input Sources</div>'
        '<div class="ag-page-sub">Agentfier accepts three types of codebase input.</div>',
        unsafe_allow_html=True,
    )

    sources = [
        (
            "🐙  GitHub Repository",
            "#6366f1",
            "Paste any public (or credentialed private) GitHub URL. "
            "Agentfier shallow-clones the repo into a local workspace for analysis.",
            [
                ("Example URL", "https://github.com/spring-projects/spring-petclinic"),
                ("Example URL", "https://github.com/gothinkster/realworld"),
                ("Works with", "Any public repo, branches, tags"),
            ],
        ),
        (
            "📁  Local Directory",
            "#10b981",
            "Enter an absolute path to a project already on your machine. "
            "The fastest option — no download required.",
            [
                ("Example", "/Users/you/projects/my-microservice"),
                ("Example", "/home/ubuntu/repos/backend"),
                ("Works with", "Any directory, including monorepos"),
            ],
        ),
        (
            "☕  JAR / WAR File",
            "#f59e0b",
            "Upload a compiled Java deployment artifact. Agentfier extracts "
            "metadata (MANIFEST.MF, pom.xml) and decompiles .class files using "
            "the CFR decompiler for deep source analysis.",
            [
                ("Supports", ".jar, .war archives"),
                ("Requires", "Java 17+ installed (for CFR decompiler)"),
                ("Auto-downloads", "CFR jar on first use"),
            ],
        ),
    ]

    for title, color, desc, details in sources:
        detail_html = "".join(
            f'<div style="color:#64748b;font-size:0.8rem;padding:2px 0;"><strong style="color:#94a3b8">{k}:</strong> {v}</div>'
            for k, v in details
        )
        st.markdown(
            f'<div class="ag-card" style="border-left:3px solid {color};margin-bottom:12px;">'
            f'<div style="font-weight:700;color:#f1f5f9;margin-bottom:6px;">{title}</div>'
            f'<div style="color:#64748b;font-size:0.87rem;margin-bottom:8px;">{desc}</div>'
            f'{detail_html}</div>',
            unsafe_allow_html=True,
        )


def _step_dimensions() -> None:
    st.markdown(
        '<div class="ag-page-title"><span class="ag-icon">🔬</span> 12 Analysis Dimensions</div>'
        '<div class="ag-page-sub">Select all or a subset of dimensions on the Analyze page. Each dimension is independent.</div>',
        unsafe_allow_html=True,
    )

    dims = [
        ("1", "⬡", "Tech Stack",       "#6366f1", "Languages, frameworks, build tools, runtime targets"),
        ("2", "📦", "Dependencies",     "#8b5cf6", "Direct/transitive deps, licenses, CVE vulnerabilities"),
        ("3", "🗄",  "Data Layer",       "#06b6d4", "Databases, ORMs, caches, message queues, migrations"),
        ("4", "🔌", "Integrations",     "#0ea5e9", "External APIs, webhooks, third-party services, brokers"),
        ("5", "🔑", "Auth & Authz",     "#10b981", "JWT/OAuth/sessions, RBAC/ABAC, identity providers"),
        ("6", "📈", "Observability",    "#84cc16", "Logging, metrics, tracing, APM, health checks"),
        ("7", "🔗", "API Architecture", "#f59e0b", "Endpoints, REST/GraphQL/gRPC, rate limiting, versioning"),
        ("8", "⚙",  "Business Logic",   "#ef4444", "Domain models, workflows, background jobs, state machines"),
        ("9", "🏗",  "Infrastructure",   "#ec4899", "Docker, K8s, CI/CD, IaC, scaling, secrets"),
        ("10","🛡",  "Security",         "#f97316", "Encryption, CORS, input validation, compliance"),
        ("11","🖥",  "Frontend",         "#a78bfa", "React/Vue/Angular, state management, SSR, build tools"),
        ("12","⚡",  "Configuration",    "#34d399", "Env vars, feature flags, multi-env strategy, secrets"),
    ]

    rows = [dims[i:i+3] for i in range(0, 12, 3)]
    for row in rows:
        cols = st.columns(3)
        for col, (num, icon, name, color, desc) in zip(cols, row):
            with col:
                st.markdown(
                    f'<div class="ag-card" style="padding:12px 14px;margin-bottom:8px;border-top:2px solid {color};">'
                    f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">'
                    f'<span style="font-size:0.65rem;font-weight:700;color:{color};background:rgba(0,0,0,0.3);'
                    f'padding:1px 5px;border-radius:3px;">#{num}</span>'
                    f'<span style="font-size:0.95rem;">{icon}</span>'
                    f'<span style="font-weight:600;color:#e2e8f0;font-size:0.85rem;">{name}</span>'
                    f'</div>'
                    f'<div style="color:#64748b;font-size:0.77rem;">{desc}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )


def _step_how_it_works() -> None:
    st.markdown(
        '<div class="ag-page-title"><span class="ag-icon">⚙</span> How Analysis Works</div>'
        '<div class="ag-page-sub">Every analyzer follows the same two-pass pattern, balancing speed with depth.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="ag-card" style="border-left:3px solid #6366f1;margin-bottom:16px;">
  <div style="font-weight:700;color:#818cf8;margin-bottom:8px;">Pass 1 — Heuristic Analysis (fast, local, free)</div>
  <div style="color:#94a3b8;font-size:0.87rem;line-height:1.7;">
    <div style="padding:3px 0;">• <strong style="color:#e2e8f0">File discovery</strong> — glob-match patterns relevant to the dimension
      (e.g. <code>**/requirements.txt</code>, <code>**/Dockerfile</code>)</div>
    <div style="padding:3px 0;">• <strong style="color:#e2e8f0">Import scanning</strong> — regex-match known library imports</div>
    <div style="padding:3px 0;">• <strong style="color:#e2e8f0">Convention detection</strong> — detect frameworks by file-structure patterns</div>
    <div style="padding:3px 0;">• <strong style="color:#e2e8f0">File-type counting</strong> — language percentage calculation</div>
    <div style="padding:3px 0;">• <strong style="color:#e2e8f0">Result</strong> — structured findings dict with evidence snippets</div>
  </div>
</div>
<div class="ag-card" style="border-left:3px solid #10b981;margin-bottom:16px;">
  <div style="font-weight:700;color:#34d399;margin-bottom:8px;">Pass 2 — Claude AI Enrichment (deep, smart)</div>
  <div style="color:#94a3b8;font-size:0.87rem;line-height:1.7;">
    <div style="padding:3px 0;">• Heuristic findings + relevant file contents sent to Claude</div>
    <div style="padding:3px 0;">• Claude confirms, corrects, and enriches the structured data</div>
    <div style="padding:3px 0;">• Response validated against a Pydantic schema (auto-retry on parse failure)</div>
    <div style="padding:3px 0;">• Model: configurable (default claude-sonnet-4-6, ~10k–18k tokens per dimension)</div>
    <div style="padding:3px 0;">• <strong style="color:#e2e8f0">Result</strong> — Pydantic model ready for display and export</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="ag-section-title">Estimated Token Usage</div>',
        unsafe_allow_html=True,
    )
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Per Dimension", "~15k tokens")
    with col2: st.metric("Full 12-dim Analysis", "~180k tokens")
    with col3: st.metric("Diagram Generation", "~30k tokens")
    with col4: st.metric("Conversion Plan", "~20k tokens")

    st.markdown(
        '<div class="ag-card" style="border-left:3px solid #f59e0b;margin-top:12px;">'
        '<div style="color:#fbbf24;font-weight:600;margin-bottom:4px;">💡 Cost tip</div>'
        '<div style="color:#64748b;font-size:0.84rem;">'
        'Select only the dimensions you need. A targeted 4-dimension analysis costs ~¼ of a full run. '
        'claude-haiku-4-5 is 10× cheaper if you need a quick first pass.</div></div>',
        unsafe_allow_html=True,
    )


def _step_live_demo() -> None:
    st.markdown(
        '<div class="ag-page-title"><span class="ag-icon">📊</span> Live Demo — Results</div>'
        '<div class="ag-page-sub">Load a pre-built Spring PetClinic analysis and explore the full Results page without an API key.</div>',
        unsafe_allow_html=True,
    )

    demo_loaded = "analysis_result" in st.session_state and \
        st.session_state.get("_demo_loaded", False)

    if demo_loaded:
        st.markdown(
            '<div class="ag-card" style="border-left:3px solid #34d399;padding:14px 18px;">'
            '<div style="color:#34d399;font-weight:600;">✓ Example analysis loaded!</div>'
            '<div style="color:#64748b;font-size:0.85rem;margin-top:4px;">'
            'Navigate to <strong style="color:#e2e8f0">📊 Results</strong> in the sidebar to explore '
            'all 12 dimension tabs, or <strong style="color:#e2e8f0">🗺 Diagrams</strong> / '
            '<strong style="color:#e2e8f0">⬡ Conversion Plan</strong> for more. '
            'Come back here when you\'re done.</div></div>',
            unsafe_allow_html=True,
        )
        if st.button("↺ Reload Example", use_container_width=False):
            _load_demo()
            st.rerun()
    else:
        st.markdown(
            '<div class="ag-card" style="padding:24px;text-align:center;">'
            '<div style="font-size:2rem;margin-bottom:10px;">🐾</div>'
            '<div style="font-weight:700;color:#f1f5f9;margin-bottom:6px;">Spring PetClinic Demo</div>'
            '<div style="color:#64748b;font-size:0.87rem;margin-bottom:16px;">'
            'A Spring Boot 3 / Java 17 veterinary clinic application — a classic, '
            'real-world reference project with a well-understood architecture.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("▶ Load Example Analysis", type="primary", use_container_width=True):
            _load_demo()
            st.rerun()

    st.markdown('<div class="ag-section-title">What you\'ll see in Results</div>', unsafe_allow_html=True)
    items = [
        ("⬡ Tech Stack",    "Java 17 + Spring Boot 3.2, Maven, Thymeleaf"),
        ("📦 Dependencies", "8 direct deps, 87 transitive, 1 medium CVE"),
        ("🗄 Data Layer",   "MySQL (prod) + H2 (dev), Hibernate, Caffeine cache"),
        ("🔑 Auth",         "Form login + HTTP Basic, RBAC via Spring Security"),
        ("🔗 API",          "10 endpoints, MVC + Actuator, Spring REST Docs"),
        ("🤖 Business",     "5 domain models, 2 workflows, 1 event pattern"),
    ]
    cols = st.columns(2)
    for i, (icon_name, detail) in enumerate(items):
        with cols[i % 2]:
            st.markdown(
                f'<div class="ag-card" style="padding:10px 14px;margin-bottom:8px;">'
                f'<div style="font-weight:600;color:#e2e8f0;font-size:0.87rem;">{icon_name}</div>'
                f'<div style="color:#64748b;font-size:0.78rem;">{detail}</div></div>',
                unsafe_allow_html=True,
            )


def _load_demo() -> None:
    st.session_state.analysis_result = _build_example_analysis()
    st.session_state.conversion_plan = _build_example_plan()
    st.session_state._demo_loaded = True


def _step_diagrams() -> None:
    st.markdown(
        '<div class="ag-page-title"><span class="ag-icon">🗺</span> Architecture Diagrams</div>'
        '<div class="ag-page-sub">Agentfier generates C4 model diagrams and user flow diagrams using Claude AI.</div>',
        unsafe_allow_html=True,
    )

    levels = [
        ("C1 — System Context",
         "#6366f1",
         "The system under analysis, its users, and the external systems it depends on. "
         "Answers: who uses it, what does it call?",
         "digraph C1 { rankdir=TB; node[shape=box,style=filled]; "
         "User[label='Pet Owner',fillcolor='#1e293b',fontcolor='#f1f5f9']; "
         "PetClinic[label='Spring PetClinic',fillcolor='#6366f1',fontcolor='white']; "
         "MySQL[label='MySQL Database',fillcolor='#1e293b',fontcolor='#f1f5f9']; "
         "Prometheus[label='Prometheus',fillcolor='#1e293b',fontcolor='#f1f5f9']; "
         "User -> PetClinic[label='HTTP']; PetClinic -> MySQL[label='JDBC']; "
         "PetClinic -> Prometheus[label='Metrics']; }"),
        ("C2 — Container",
         "#10b981",
         "High-level technical building blocks: web app, API, database, cache. "
         "Answers: what are the deployable units?",
         "digraph C2 { rankdir=LR; node[shape=box,style=filled]; "
         "Web[label='Spring MVC\\nThymeleaf',fillcolor='#6366f1',fontcolor='white']; "
         "DB[label='MySQL',fillcolor='#1e293b',fontcolor='#f1f5f9']; "
         "Cache[label='Caffeine',fillcolor='#1e293b',fontcolor='#f1f5f9']; "
         "Actuator[label='Actuator\\nPrometheus',fillcolor='#1e293b',fontcolor='#f1f5f9']; "
         "Web -> DB; Web -> Cache; Web -> Actuator; }"),
        ("C3 — Component",
         "#f59e0b",
         "Internal components inside a container: controllers, services, repositories. "
         "Answers: how does the code hang together?",
         "digraph C3 { rankdir=TB; node[shape=box,style=filled]; "
         "OC[label='OwnerController',fillcolor='#6366f1',fontcolor='white']; "
         "OS[label='OwnerService',fillcolor='#1e293b',fontcolor='#f1f5f9']; "
         "OR[label='OwnerRepository',fillcolor='#1e293b',fontcolor='#f1f5f9']; "
         "VC[label='VetController',fillcolor='#6366f1',fontcolor='white']; "
         "VR[label='VetRepository',fillcolor='#1e293b',fontcolor='#f1f5f9']; "
         "OC -> OS -> OR; VC -> VR; }"),
    ]

    for title, color, desc, _ in levels:
        st.markdown(
            f'<div class="ag-card" style="border-left:3px solid {color};margin-bottom:10px;">'
            f'<div style="font-weight:700;color:#f1f5f9;margin-bottom:4px;">{title}</div>'
            f'<div style="color:#64748b;font-size:0.85rem;">{desc}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="ag-card" style="border-left:3px solid #8b5cf6;margin-top:8px;">'
        '<div style="font-weight:700;color:#a78bfa;margin-bottom:4px;">🔀 User Flow Diagram</div>'
        '<div style="color:#64748b;font-size:0.85rem;">'
        'Visualizes the primary user journeys through the system, derived from '
        'API endpoints and business logic workflows. Rendered as a Graphviz flowchart.</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ag-card" style="border-left:3px solid #334155;margin-top:8px;">'
        '<div style="color:#475569;font-size:0.83rem;">'
        '💡 Diagrams are rendered as SVG/PNG via the system Graphviz package. '
        'If Graphviz is not installed, the raw DOT source is shown instead '
        '(<code>brew install graphviz</code> on macOS, <code>sudo apt install graphviz</code> on Linux).'
        '</div></div>',
        unsafe_allow_html=True,
    )


def _step_conversion_plan() -> None:
    st.markdown(
        '<div class="ag-page-title"><span class="ag-icon">🤖</span> Agent Conversion Plan</div>'
        '<div class="ag-page-sub">A phased migration roadmap from traditional architecture to an agent-native system.</div>',
        unsafe_allow_html=True,
    )

    demo_plan = "conversion_plan" in st.session_state and st.session_state.get("_demo_loaded", False)
    if demo_plan:
        st.markdown(
            '<div class="ag-card" style="border-left:3px solid #34d399;padding:12px 16px;">'
            '<div style="color:#34d399;font-size:0.85rem;">✓ Example conversion plan is loaded. '
            'Navigate to <strong style="color:#e2e8f0">⬡ Conversion Plan</strong> to see it in full.</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="ag-card" style="border-left:3px solid #f59e0b;padding:12px 16px;">'
            '<div style="color:#fbbf24;font-size:0.85rem;">💡 Load the example on Step 5 first to see a pre-built conversion plan.</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="ag-section-title">Output Structure</div>', unsafe_allow_html=True)
    sections = [
        ("🤖 Agent Decomposition",  "Each proposed agent: name, responsibilities, tool list"),
        ("📡 Communication Topology", "How agents communicate (hub-and-spoke, mesh, pipeline)"),
        ("🎯 Orchestration Pattern", "Supervisor / coordinator style and agent relationships"),
        ("🗺 Migration Phases",      "Ordered phases with tasks, risks, and acceptance criteria"),
        ("⚠ Risk Assessment",       "Overall migration risk narrative with mitigation strategies"),
    ]
    for title, desc in sections:
        st.markdown(
            f'<div class="ag-card" style="padding:10px 14px;margin-bottom:8px;">'
            f'<div style="font-weight:600;color:#e2e8f0;font-size:0.87rem;">{title}</div>'
            f'<div style="color:#64748b;font-size:0.78rem;">{desc}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="ag-section-title">Get Started</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ag-card" style="border-top:2px solid #6366f1;padding:20px;">'
        '<div style="font-weight:700;color:#f1f5f9;margin-bottom:8px;">You\'re ready! Here\'s the workflow:</div>'
        '<div style="color:#94a3b8;font-size:0.87rem;line-height:1.8;">'
        '1️⃣  Enter your <strong style="color:#e2e8f0">Anthropic API key</strong> in the sidebar (session-only, never stored)<br>'
        '2️⃣  Go to <strong style="color:#e2e8f0">⬡ Analyze</strong> — choose an input source and select dimensions<br>'
        '3️⃣  Click <strong style="color:#818cf8">▶ Start Analysis</strong> and watch each dimension complete<br>'
        '4️⃣  Explore <strong style="color:#e2e8f0">📊 Results</strong> — browse 12 tabs, download YAML/JSON spec<br>'
        '5️⃣  Go to <strong style="color:#e2e8f0">🗺 Diagrams</strong> — generate C4 architecture diagrams<br>'
        '6️⃣  Go to <strong style="color:#e2e8f0">⬡ Conversion Plan</strong> — generate your agent migration roadmap'
        '</div></div>',
        unsafe_allow_html=True,
    )


# ── Main render ───────────────────────────────────────────────────────────────

def render() -> None:
    if "guide_step" not in st.session_state:
        st.session_state.guide_step = 0

    step = st.session_state.guide_step

    st.markdown(
        f'<div class="ag-page-title">'
        f'<span class="ag-icon">{STEP_ICONS[step]}</span> Interactive Tour'
        f'</div>'
        f'<div class="ag-page-sub">A guided walkthrough of all Agentfier capabilities.</div>',
        unsafe_allow_html=True,
    )

    _step_indicator(step)
    st.markdown('<div style="border-top:1px solid #1e293b;margin-bottom:20px;"></div>', unsafe_allow_html=True)

    if step == 0:
        _step_welcome()
    elif step == 1:
        _step_input_sources()
    elif step == 2:
        _step_dimensions()
    elif step == 3:
        _step_how_it_works()
    elif step == 4:
        _step_live_demo()
    elif step == 5:
        _step_diagrams()
    elif step == 6:
        _step_conversion_plan()

    st.markdown('<div style="border-top:1px solid #1e293b;margin-top:24px;margin-bottom:8px;"></div>', unsafe_allow_html=True)
    _nav_buttons(step)
