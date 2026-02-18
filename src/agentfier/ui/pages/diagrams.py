import os
import streamlit as st
from agentfier.claude.client import ClaudeClient
from agentfier.diagrams.c4_generator import C4DiagramGenerator
from agentfier.diagrams.flow_generator import FlowDiagramGenerator


def render():
    st.header("Architecture Diagrams")

    if "analysis_result" not in st.session_state:
        st.info("No analysis results yet. Go to the Analyze page to run an analysis.")
        return

    analysis = st.session_state.analysis_result
    api_key = st.session_state.get("api_key", os.environ.get("ANTHROPIC_API_KEY", ""))
    model = st.session_state.get("model", "claude-sonnet-4-5-20250929")
    output_dir = os.environ.get("OUTPUT_DIR", "data/outputs")

    if not api_key:
        st.warning("API key required for diagram generation.")
        return

    if "diagrams" not in st.session_state:
        st.session_state.diagrams = {}

    if st.button("Generate Diagrams", type="primary"):
        claude = ClaudeClient(api_key=api_key, model=model)

        with st.status("Generating C4 diagrams...", expanded=True) as status:
            c4_gen = C4DiagramGenerator(claude, output_dir)
            c4_results = c4_gen.generate_all(analysis)
            st.session_state.diagrams.update(
                {f"c4_{k}": str(v) for k, v in c4_results.items()}
            )
            status.update(
                label=f"Generated {len(c4_results)} C4 diagrams", state="complete"
            )

        with st.status("Generating user flow diagram...", expanded=True) as status:
            flow_gen = FlowDiagramGenerator(claude, output_dir)
            flow_path = flow_gen.generate(analysis)
            if flow_path:
                st.session_state.diagrams["user_flow"] = str(flow_path)
            status.update(label="Flow diagram generated", state="complete")

    # Display diagrams
    if st.session_state.diagrams:
        st.subheader("C4 Architecture Diagrams")
        c4_tab_names = []
        c4_paths = []
        for level in ["context", "container", "component"]:
            key = f"c4_{level}"
            if key in st.session_state.diagrams:
                c4_tab_names.append(level.title())
                c4_paths.append(st.session_state.diagrams[key])

        if c4_tab_names:
            tabs = st.tabs(c4_tab_names)
            for tab, path in zip(tabs, c4_paths):
                with tab:
                    if path.endswith(".svg") or path.endswith(".png"):
                        st.image(path, use_container_width=True)
                    elif path.endswith(".dot"):
                        with open(path) as f:
                            st.code(f.read(), language="dot")
                        st.caption(
                            "Graphviz not available - showing DOT source. "
                            "Install graphviz to render."
                        )

        if "user_flow" in st.session_state.diagrams:
            st.subheader("User Flow Diagram")
            flow_path = st.session_state.diagrams["user_flow"]
            if flow_path.endswith(".svg") or flow_path.endswith(".png"):
                st.image(flow_path, use_container_width=True)
            elif flow_path.endswith(".dot"):
                with open(flow_path) as f:
                    st.code(f.read(), language="dot")
    else:
        st.info(
            "Click 'Generate Diagrams' to create C4 architecture and user flow diagrams."
        )
