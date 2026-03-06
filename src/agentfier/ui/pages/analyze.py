import os
import streamlit as st
from datetime import datetime
from agentfier.claude.client import ClaudeClient
from agentfier.models.analysis import AnalysisResult
from agentfier.models.enums import InputType
from agentfier.ingestors.local_ingestor import LocalIngestor
from agentfier.ingestors.github_ingestor import GitHubIngestor
from agentfier.ingestors.jar_ingestor import JarIngestor

ANALYZER_REGISTRY = [
    ("tech_stack",       "agentfier.analyzers.tech_stack",       "TechStackAnalyzer",       "Technology Stack"),
    ("dependencies",     "agentfier.analyzers.dependencies",     "DependencyAnalyzer",       "Dependencies"),
    ("data_layer",       "agentfier.analyzers.data_layer",       "DataLayerAnalyzer",        "Data Layer"),
    ("integrations",     "agentfier.analyzers.integrations",     "IntegrationAnalyzer",      "Integration Points"),
    ("auth",             "agentfier.analyzers.auth",             "AuthAnalyzer",             "Auth & Authorization"),
    ("observability",    "agentfier.analyzers.observability",    "ObservabilityAnalyzer",    "Observability"),
    ("api_architecture", "agentfier.analyzers.api_architecture", "ApiArchitectureAnalyzer",  "API Architecture"),
    ("business_logic",   "agentfier.analyzers.business_logic",   "BusinessLogicAnalyzer",    "Business Logic"),
    ("infrastructure",   "agentfier.analyzers.infrastructure",   "InfrastructureAnalyzer",   "Infrastructure"),
    ("security",         "agentfier.analyzers.security",         "SecurityAnalyzer",         "Security & Compliance"),
    ("frontend",         "agentfier.analyzers.frontend",         "FrontendAnalyzer",         "Frontend Architecture"),
    ("configuration",    "agentfier.analyzers.configuration",    "ConfigurationAnalyzer",    "Configuration Mgmt"),
]

_DIM_ICONS = {
    "tech_stack": "⬡",
    "dependencies": "📦",
    "data_layer": "🗄",
    "integrations": "🔌",
    "auth": "🔑",
    "observability": "📈",
    "api_architecture": "🔗",
    "business_logic": "⚙",
    "infrastructure": "🏗",
    "security": "🛡",
    "frontend": "🖥",
    "configuration": "⚡",
}


def _get_analyzer_class(module_path: str, class_name: str):
    import importlib
    mod = importlib.import_module(module_path)
    return getattr(mod, class_name)


def render():
    st.markdown(
        """
<div class="ag-page-title">
  <span class="ag-icon">🔬</span> Codebase Analysis
</div>
<div class="ag-page-sub">
  Analyze your codebase across 12 architectural dimensions to generate an agent-native conversion specification.
</div>
""",
        unsafe_allow_html=True,
    )

    # ── Input source ──────────────────────────────────────────────────────────
    st.markdown('<div class="ag-section-title">Input Source</div>', unsafe_allow_html=True)

    input_type = st.radio(
        "Select input type:",
        [InputType.GITHUB.value, InputType.JAR_WAR.value, InputType.LOCAL.value],
        format_func=lambda x: {
            "github":  "⎔  GitHub Repository URL",
            "jar_war": "☕  JAR / WAR File Upload",
            "local":   "📁  Local Directory Path",
        }[x],
        horizontal=True,
        label_visibility="collapsed",
    )

    source_value = None
    uploaded_file = None

    if input_type == InputType.GITHUB.value:
        source_value = st.text_input(
            "GitHub URL",
            placeholder="https://github.com/user/repo",
            label_visibility="collapsed",
        )
    elif input_type == InputType.JAR_WAR.value:
        uploaded_file = st.file_uploader("Upload JAR/WAR file", type=["jar", "war"])
        if uploaded_file:
            source_value = uploaded_file.name
    elif input_type == InputType.LOCAL.value:
        source_value = st.text_input(
            "Local path",
            placeholder="/path/to/your/project",
            label_visibility="collapsed",
        )

    # ── Dimension selection ──────────────────────────────────────────────────
    st.markdown('<div class="ag-section-title">Analysis Dimensions</div>', unsafe_allow_html=True)

    col1, col2, _spacer = st.columns([1, 1, 6])
    with col1:
        if st.button("Select All", use_container_width=True):
            st.session_state.selected_dims = [r[0] for r in ANALYZER_REGISTRY]
    with col2:
        if st.button("Clear All", use_container_width=True):
            st.session_state.selected_dims = []

    if "selected_dims" not in st.session_state:
        st.session_state.selected_dims = [r[0] for r in ANALYZER_REGISTRY]

    cols = st.columns(4)
    selected = []
    for i, (dim_key, _, _, display_name) in enumerate(ANALYZER_REGISTRY):
        with cols[i % 4]:
            icon = _DIM_ICONS.get(dim_key, "•")
            checked = st.checkbox(
                f"{icon} {display_name}",
                value=dim_key in st.session_state.selected_dims,
                key=f"dim_{dim_key}",
            )
            if checked:
                selected.append(dim_key)
    st.session_state.selected_dims = selected

    # ── Selected count indicator ─────────────────────────────────────────────
    count = len(selected)
    badge_cls = "ag-badge-indigo" if count > 0 else "ag-badge"
    st.markdown(
        f'<div style="margin-top:6px;margin-bottom:2px;">'
        f'<span class="ag-badge {badge_cls}">{count} / {len(ANALYZER_REGISTRY)} dimensions selected</span>'
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── Launch analysis ──────────────────────────────────────────────────────
    st.markdown('<div style="border-top:1px solid #1e293b;margin:18px 0 14px;"></div>', unsafe_allow_html=True)

    api_key = st.session_state.get("api_key", "")

    if not api_key:
        st.markdown(
            '<div class="ag-card"><div class="ag-card-header">⚠ API Key Required</div>'
            '<div style="color:#94a3b8;font-size:0.87rem;">Set your Anthropic API key in '
            'Enter your <strong>Anthropic API key</strong> in the sidebar to get started.</div></div>',
            unsafe_allow_html=True,
        )

    can_start = bool(source_value and api_key and selected)

    if st.button("▶  Start Analysis", type="primary", disabled=not can_start, use_container_width=False):
        _run_analysis(input_type, source_value, uploaded_file, selected, api_key)


def _run_analysis(input_type, source_value, uploaded_file, selected_dims, api_key):
    model = st.session_state.get("model", "claude-sonnet-4-6")
    workspace_dir = os.environ.get("WORKSPACE_DIR", "data/workspaces")

    claude = ClaudeClient(api_key=api_key, model=model)

    # Phase 1: Ingestion
    with st.status("⬡  Ingesting source…", expanded=True) as status:
        try:
            if input_type == InputType.GITHUB.value:
                ingestor = GitHubIngestor(workspace_dir=workspace_dir)
                ingest_result = ingestor.ingest(source_value)
            elif input_type == InputType.JAR_WAR.value:
                ingestor = JarIngestor(workspace_dir=workspace_dir)
                ingest_result = ingestor.ingest(
                    uploaded_file.getvalue(), filename=uploaded_file.name
                )
            else:
                ingestor = LocalIngestor()
                ingest_result = ingestor.ingest(source_value)

            st.markdown(
                f'<span class="ag-badge ag-badge-green">✓ {ingest_result.total_files} files '
                f"({ingest_result.total_size_bytes / 1024:.0f} KB)</span>",
                unsafe_allow_html=True,
            )
            status.update(label="✓  Ingestion complete", state="complete")
        except Exception as e:
            status.update(label=f"✗  Ingestion failed: {e}", state="error")
            st.error(f"Failed to ingest source: {e}")
            return

    # Phase 2: Analysis
    analysis = AnalysisResult(
        input_source=source_value,
        input_type=input_type,
        analyzed_at=datetime.now(),
    )

    analyzers_to_run = [
        (dim_key, mod_path, cls_name, display_name)
        for dim_key, mod_path, cls_name, display_name in ANALYZER_REGISTRY
        if dim_key in selected_dims
    ]

    progress_bar = st.progress(0, text="Initializing analyzers…")
    total = len(analyzers_to_run)

    for i, (dim_key, mod_path, cls_name, display_name) in enumerate(analyzers_to_run):
        icon = _DIM_ICONS.get(dim_key, "•")
        progress_bar.progress(i / total, text=f"{icon} Analyzing {display_name}… ({i + 1}/{total})")

        with st.status(f"{icon} {display_name}", expanded=False) as dim_status:
            try:
                analyzer_class = _get_analyzer_class(mod_path, cls_name)
                analyzer = analyzer_class(claude, ingest_result.workspace_path)
                result = analyzer.analyze()
                setattr(analysis, dim_key, result)
                dim_status.update(label=f"✓  {display_name}", state="complete")
            except Exception as e:
                dim_status.update(label=f"✗  {display_name} — {e}", state="error")
                st.warning(f"Analyzer '{display_name}' failed: {e}")

    progress_bar.progress(1.0, text="Analysis complete!")

    st.session_state.analysis_result = analysis
    st.session_state.ingest_result = ingest_result

    st.markdown(
        '<div class="ag-card" style="border-left:3px solid #10b981;">'
        '<div style="color:#34d399;font-weight:600;margin-bottom:4px;">✓ Analysis complete</div>'
        '<div style="color:#64748b;font-size:0.85rem;">Navigate to <strong>Results</strong>, '
        '<strong>Diagrams</strong>, or <strong>Conversion Plan</strong> to view outputs.</div>'
        "</div>",
        unsafe_allow_html=True,
    )
