import os
import streamlit as st
import yaml
from agentfier.claude.client import ClaudeClient
from agentfier.output.conversion_plan import ConversionPlanGenerator
from agentfier.output.api_doc_generator import ApiDocGenerator


def render():
    st.header("Agent-Native Conversion Plan")

    if "analysis_result" not in st.session_state:
        st.info("No analysis results yet. Go to the Analyze page to run an analysis.")
        return

    analysis = st.session_state.analysis_result
    api_key = st.session_state.get("api_key", os.environ.get("ANTHROPIC_API_KEY", ""))
    model = st.session_state.get("model", "claude-sonnet-4-5-20250929")

    if not api_key:
        st.warning("API key required for conversion plan generation.")
        return

    if "conversion_plan" not in st.session_state:
        st.session_state.conversion_plan = None

    if st.button("Generate Conversion Plan", type="primary"):
        claude = ClaudeClient(api_key=api_key, model=model)

        with st.status("Generating agent-native conversion plan...", expanded=True) as status:
            gen = ConversionPlanGenerator(claude)
            plan = gen.generate(analysis)
            if plan:
                st.session_state.conversion_plan = plan
                status.update(label="Conversion plan generated", state="complete")
            else:
                status.update(label="Failed to generate conversion plan", state="error")

    plan = st.session_state.conversion_plan
    if plan:
        # Download
        plan_yaml = yaml.dump(plan.model_dump(), default_flow_style=False, sort_keys=False)
        st.download_button("Download Plan (YAML)", plan_yaml, "conversion_plan.yaml", "text/yaml")

        st.divider()

        # Agent Decomposition
        with st.expander("Agent Decomposition", expanded=True):
            if plan.agent_decomposition:
                for agent in plan.agent_decomposition:
                    name = getattr(agent, "name", str(agent))
                    responsibilities = getattr(agent, "responsibilities", [])
                    tools = getattr(agent, "tools", [])
                    st.markdown(f"**{name}**")
                    if responsibilities:
                        st.write("Responsibilities:")
                        for r in responsibilities:
                            st.write(f"  - {r}")
                    if tools:
                        st.write(f"Tools: {', '.join(tools)}")
                    st.divider()

        # Communication Topology
        with st.expander("Communication Topology"):
            st.write(plan.communication_topology)

        # Orchestration Pattern
        with st.expander("Orchestration Pattern"):
            st.write(plan.orchestration_pattern)

        # Migration Roadmap
        with st.expander("Migration Roadmap", expanded=True):
            if plan.migration_phases:
                for phase in plan.migration_phases:
                    phase_num = getattr(phase, "phase", "?")
                    name = getattr(phase, "name", "")
                    desc = getattr(phase, "description", "")
                    tasks = getattr(phase, "tasks", [])
                    risks = getattr(phase, "risks", [])

                    st.markdown(f"### Phase {phase_num}: {name}")
                    st.write(desc)
                    if tasks:
                        st.write("**Tasks:**")
                        for t in tasks:
                            st.write(f"- {t}")
                    if risks:
                        st.write("**Risks:**")
                        for r in risks:
                            st.warning(r)

        # Risk Assessment
        with st.expander("Risk Assessment"):
            st.write(plan.risk_assessment)

        # API Documentation
        st.divider()
        st.subheader("API Documentation")
        api_gen = ApiDocGenerator()
        api_doc = api_gen.generate(analysis)
        if api_doc:
            st.markdown(api_doc)
            st.download_button(
                "Download API Doc", api_doc, "api_documentation.md", "text/markdown"
            )
        else:
            st.info("No API architecture data available for documentation generation.")
    else:
        st.info(
            "Click 'Generate Conversion Plan' to create an agent-native conversion strategy."
        )
