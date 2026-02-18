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
    ("tech_stack", "agentfier.analyzers.tech_stack", "TechStackAnalyzer", "Technology Stack"),
    ("dependencies", "agentfier.analyzers.dependencies", "DependencyAnalyzer", "Dependencies"),
    ("data_layer", "agentfier.analyzers.data_layer", "DataLayerAnalyzer", "Data Layer"),
    ("integrations", "agentfier.analyzers.integrations", "IntegrationAnalyzer", "Integration Points"),
    ("auth", "agentfier.analyzers.auth", "AuthAnalyzer", "Auth & Authorization"),
    ("observability", "agentfier.analyzers.observability", "ObservabilityAnalyzer", "Observability"),
    ("api_architecture", "agentfier.analyzers.api_architecture", "ApiArchitectureAnalyzer", "API Architecture"),
    ("business_logic", "agentfier.analyzers.business_logic", "BusinessLogicAnalyzer", "Business Logic"),
    ("infrastructure", "agentfier.analyzers.infrastructure", "InfrastructureAnalyzer", "Infrastructure"),
    ("security", "agentfier.analyzers.security", "SecurityAnalyzer", "Security & Compliance"),
    ("frontend", "agentfier.analyzers.frontend", "FrontendAnalyzer", "Frontend Architecture"),
    ("configuration", "agentfier.analyzers.configuration", "ConfigurationAnalyzer", "Configuration Mgmt"),
]


def _get_analyzer_class(module_path: str, class_name: str):
    import importlib
    mod = importlib.import_module(module_path)
    return getattr(mod, class_name)


def render():
    st.header("Codebase Analysis")
    st.markdown(
        "Analyze your codebase across 12 architectural dimensions to generate "
        "an agent-native conversion specification."
    )

    # Input source selection
    st.subheader("Input Source")
    input_type = st.radio(
        "Select input type:",
        [InputType.GITHUB.value, InputType.JAR_WAR.value, InputType.LOCAL.value],
        format_func=lambda x: {
            "github": "GitHub Repository URL",
            "jar_war": "JAR/WAR File Upload",
            "local": "Local Directory Path",
        }[x],
        horizontal=True,
    )

    source_value = None
    uploaded_file = None

    if input_type == InputType.GITHUB.value:
        source_value = st.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/user/repo",
        )
    elif input_type == InputType.JAR_WAR.value:
        uploaded_file = st.file_uploader("Upload JAR/WAR file", type=["jar", "war"])
        if uploaded_file:
            source_value = uploaded_file.name
    elif input_type == InputType.LOCAL.value:
        source_value = st.text_input(
            "Local Directory Path",
            placeholder="/path/to/your/project",
        )

    # Dimension selection
    st.subheader("Analysis Dimensions")
    col1, col2 = st.columns(2)
    with col1:
        select_all = st.button("Select All")
    with col2:
        deselect_all = st.button("Deselect All")

    if select_all:
        st.session_state.selected_dims = [r[0] for r in ANALYZER_REGISTRY]
    if deselect_all:
        st.session_state.selected_dims = []

    if "selected_dims" not in st.session_state:
        st.session_state.selected_dims = [r[0] for r in ANALYZER_REGISTRY]

    cols = st.columns(3)
    selected = []
    for i, (dim_key, _, _, display_name) in enumerate(ANALYZER_REGISTRY):
        with cols[i % 3]:
            checked = st.checkbox(
                display_name,
                value=dim_key in st.session_state.selected_dims,
                key=f"dim_{dim_key}",
            )
            if checked:
                selected.append(dim_key)
    st.session_state.selected_dims = selected

    # Start Analysis
    st.divider()
    api_key = st.session_state.get("api_key", os.environ.get("ANTHROPIC_API_KEY", ""))

    if not api_key:
        st.warning(
            "Please set your Anthropic API key in the sidebar settings "
            "or ANTHROPIC_API_KEY environment variable."
        )

    can_start = source_value and api_key and selected

    if st.button("Start Analysis", type="primary", disabled=not can_start):
        _run_analysis(input_type, source_value, uploaded_file, selected, api_key)


def _run_analysis(input_type, source_value, uploaded_file, selected_dims, api_key):
    model = st.session_state.get("model", "claude-sonnet-4-5-20250929")
    workspace_dir = os.environ.get("WORKSPACE_DIR", "data/workspaces")

    claude = ClaudeClient(api_key=api_key, model=model)

    # Phase 1: Ingestion
    with st.status("Ingesting source...", expanded=True) as status:
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

            st.write(
                f"Ingested **{ingest_result.total_files}** files "
                f"({ingest_result.total_size_bytes / 1024:.0f} KB)"
            )
            status.update(label="Ingestion complete", state="complete")
        except Exception as e:
            status.update(label=f"Ingestion failed: {e}", state="error")
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

    progress_bar = st.progress(0, text="Starting analysis...")
    total = len(analyzers_to_run)

    for i, (dim_key, mod_path, cls_name, display_name) in enumerate(analyzers_to_run):
        progress_bar.progress(i / total, text=f"Analyzing {display_name}... ({i + 1}/{total})")

        with st.status(f"Analyzing {display_name}...", expanded=False) as dim_status:
            try:
                analyzer_class = _get_analyzer_class(mod_path, cls_name)
                analyzer = analyzer_class(claude, ingest_result.workspace_path)
                result = analyzer.analyze()
                setattr(analysis, dim_key, result)
                dim_status.update(label=f"{display_name} - Complete", state="complete")
            except Exception as e:
                dim_status.update(label=f"{display_name} - Error: {e}", state="error")
                st.warning(f"Analyzer '{display_name}' failed: {e}")

    progress_bar.progress(1.0, text="Analysis complete!")

    st.session_state.analysis_result = analysis
    st.session_state.ingest_result = ingest_result

    st.success(
        "Analysis complete! Navigate to the Results, Diagrams, "
        "or Conversion Plan pages to view outputs."
    )
