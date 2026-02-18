import streamlit as st
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agentfier.ui.pages import analyze, results, diagrams, conversion

st.set_page_config(
    page_title="Agentfier - Codebase Analyzer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    st.sidebar.title("Agentfier")
    st.sidebar.markdown("*Codebase → Agent-Native*")
    st.sidebar.divider()

    page = st.sidebar.radio(
        "Navigation",
        ["Analyze", "Results", "Diagrams", "Conversion Plan"],
        index=0,
    )

    # Sidebar settings
    with st.sidebar.expander("Settings", expanded=False):
        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            value=os.environ.get("ANTHROPIC_API_KEY", ""),
        )
        model = st.selectbox(
            "Model",
            [
                "claude-sonnet-4-5-20250929",
                "claude-opus-4-6",
                "claude-haiku-4-5-20251001",
            ],
        )
        max_files = st.slider("Max Files to Analyze", 50, 1000, 500, step=50)

        if api_key:
            st.session_state.api_key = api_key
        st.session_state.model = model
        st.session_state.max_files = max_files

    st.sidebar.divider()
    st.sidebar.caption("Agentfier v0.1.0")

    # Route to selected page
    if page == "Analyze":
        analyze.render()
    elif page == "Results":
        results.render()
    elif page == "Diagrams":
        diagrams.render()
    elif page == "Conversion Plan":
        conversion.render()


if __name__ == "__main__":
    main()
