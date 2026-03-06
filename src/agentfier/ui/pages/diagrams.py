import os
import streamlit as st
from agentfier.claude.client import ClaudeClient
from agentfier.diagrams.c4_generator import C4DiagramGenerator
from agentfier.diagrams.flow_generator import FlowDiagramGenerator


def render():
    st.markdown(
        """
<div class="ag-page-title">
  <span class="ag-icon">🗺</span> Architecture Diagrams
</div>
<div class="ag-page-sub">Generate C4 architecture diagrams (Context, Container, Component) and user flow diagrams using Claude AI.</div>
""",
        unsafe_allow_html=True,
    )

    if "analysis_result" not in st.session_state:
        st.info("No analysis results yet. Go to the **Analyze** page to run an analysis.")
        return

    analysis = st.session_state.analysis_result
    api_key = st.session_state.get("api_key", "")
    model = st.session_state.get("model", "claude-sonnet-4-6")
    output_dir = os.environ.get("OUTPUT_DIR", "data/outputs")

    if not api_key:
        st.markdown(
            '<div class="ag-card" style="border-left:3px solid #f59e0b;">'
            '<div style="color:#fbbf24;font-weight:600;">⚠ API Key Required</div>'
            '<div style="color:#64748b;font-size:0.87rem;margin-top:4px">Set your key in ⚙ Settings.</div>'
            "</div>",
            unsafe_allow_html=True,
        )
        return

    if "diagrams" not in st.session_state:
        st.session_state.diagrams = {}

    col1, _ = st.columns([1, 5])
    with col1:
        generate = st.button("▶ Generate Diagrams", type="primary", use_container_width=True)

    if generate:
        claude = ClaudeClient(api_key=api_key, model=model)

        with st.status("🗺 Generating C4 diagrams…", expanded=True) as status:
            c4_gen = C4DiagramGenerator(claude, output_dir)
            c4_results = c4_gen.generate_all(analysis)
            st.session_state.diagrams.update(
                {f"c4_{k}": str(v) for k, v in c4_results.items()}
            )
            status.update(
                label=f"✓ Generated {len(c4_results)} C4 diagrams",
                state="complete",
            )

        with st.status("🔀 Generating user flow diagram…", expanded=True) as status:
            flow_gen = FlowDiagramGenerator(claude, output_dir)
            flow_path = flow_gen.generate(analysis)
            if flow_path:
                st.session_state.diagrams["user_flow"] = str(flow_path)
            status.update(
                label="✓ Flow diagram generated" if flow_path else "⚠ Could not generate flow diagram",
                state="complete" if flow_path else "error",
            )

    # ── Display diagrams ──────────────────────────────────────────────────────
    if st.session_state.diagrams:
        c4_levels = [
            (level, f"c4_{level}")
            for level in ["context", "container", "component"]
            if f"c4_{level}" in st.session_state.diagrams
        ]

        if c4_levels:
            st.markdown('<div class="ag-section-title">C4 Architecture Diagrams</div>', unsafe_allow_html=True)
            tab_names = [level.title() for level, _ in c4_levels]
            tabs = st.tabs(tab_names)
            for tab, (level, key) in zip(tabs, c4_levels):
                with tab:
                    path = st.session_state.diagrams[key]
                    _show_diagram(path, f"C4 {level.title()} Diagram")

        if "user_flow" in st.session_state.diagrams:
            st.markdown('<div class="ag-section-title">User Flow Diagram</div>', unsafe_allow_html=True)
            _show_diagram(st.session_state.diagrams["user_flow"], "User Flow")
    else:
        st.markdown(
            '<div class="ag-card" style="text-align:center;padding:30px;">'
            '<div style="font-size:2rem;margin-bottom:10px;">🗺</div>'
            '<div style="color:#64748b;">Click <strong>▶ Generate Diagrams</strong> to create '
            "C4 architecture and user flow diagrams.</div>"
            "</div>",
            unsafe_allow_html=True,
        )


def _show_diagram(path: str, title: str) -> None:
    if path.endswith(".svg") or path.endswith(".png"):
        st.image(path, use_container_width=True)
    elif path.endswith(".dot"):
        st.markdown(
            f'<div class="ag-card" style="padding:12px 16px;">'
            f'<div class="ag-card-header">⚠ Graphviz not installed — showing DOT source for <em>{title}</em></div>'
            f"</div>",
            unsafe_allow_html=True,
        )
        with open(path) as f:
            st.code(f.read(), language="dot")
        st.caption("Install the `graphviz` system package to render diagrams as images.")
