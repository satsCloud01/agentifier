import streamlit as st
import yaml
from agentfier.claude.client import ClaudeClient
from agentfier.output.conversion_plan import ConversionPlanGenerator
from agentfier.output.api_doc_generator import ApiDocGenerator


def _badge(label: str, variant: str = "") -> str:
    cls = f"ag-badge {f'ag-badge-{variant}' if variant else ''}"
    return f'<span class="{cls}">{label}</span>'


def _section(title: str) -> None:
    st.markdown(f'<div class="ag-section-title">{title}</div>', unsafe_allow_html=True)


def render():
    st.markdown(
        """
<div class="ag-page-title">
  <span class="ag-icon">⬡</span> Agent-Native Conversion Plan
</div>
<div class="ag-page-sub">Generate a detailed migration roadmap to transform this codebase into an agent-native architecture.</div>
""",
        unsafe_allow_html=True,
    )

    if "analysis_result" not in st.session_state:
        st.info("No analysis results yet. Go to the **Analyze** page to run an analysis.")
        return

    analysis = st.session_state.analysis_result
    api_key = st.session_state.get("api_key", "")
    model = st.session_state.get("model", "claude-sonnet-4-6")

    if not api_key:
        st.markdown(
            '<div class="ag-card" style="border-left:3px solid #f59e0b;">'
            '<div style="color:#fbbf24;font-weight:600;">⚠ API Key Required</div>'
            '<div style="color:#64748b;font-size:0.87rem;margin-top:4px">Set your key in ⚙ Settings.</div>'
            "</div>",
            unsafe_allow_html=True,
        )
        return

    if "conversion_plan" not in st.session_state:
        st.session_state.conversion_plan = None

    col1, _rest = st.columns([2, 5])
    with col1:
        generate = st.button("▶ Generate Conversion Plan", type="primary", use_container_width=True)

    if generate:
        claude = ClaudeClient(api_key=api_key, model=model)
        with st.status("⬡ Generating agent-native conversion plan…", expanded=True) as status:
            gen = ConversionPlanGenerator(claude)
            plan = gen.generate(analysis)
            if plan:
                st.session_state.conversion_plan = plan
                status.update(label="✓ Conversion plan generated", state="complete")
            else:
                status.update(label="✗ Failed to generate conversion plan", state="error")

    plan = st.session_state.conversion_plan
    if not plan:
        st.markdown(
            '<div class="ag-card" style="text-align:center;padding:30px;">'
            '<div style="font-size:2rem;margin-bottom:10px;">⬡</div>'
            '<div style="color:#64748b;">Click <strong>▶ Generate Conversion Plan</strong> to create '
            "an agent-native migration strategy.</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        return

    # ── Download ──────────────────────────────────────────────────────────────
    plan_yaml = yaml.dump(plan.model_dump(), default_flow_style=False, sort_keys=False)
    col1, _rest = st.columns([2, 6])
    with col1:
        st.download_button("⬇ Download Plan (YAML)", plan_yaml, "conversion_plan.yaml", "text/yaml", use_container_width=True)

    st.markdown('<div style="border-top:1px solid #1e293b;margin:16px 0;"></div>', unsafe_allow_html=True)

    # ── Summary badges ────────────────────────────────────────────────────────
    agent_count = len(plan.agent_decomposition)
    phase_count = len(plan.migration_phases)
    st.markdown(
        f'<div class="ag-stat-row">'
        f'<div class="ag-stat"><div class="ag-stat-label">Agents</div>'
        f'<div class="ag-stat-value">{agent_count}</div>'
        f'<div class="ag-stat-sub">specialized agents</div></div>'
        f'<div class="ag-stat"><div class="ag-stat-label">Migration Phases</div>'
        f'<div class="ag-stat-value">{phase_count}</div>'
        f'<div class="ag-stat-sub">phases</div></div>'
        f'<div class="ag-stat"><div class="ag-stat-label">Topology</div>'
        f'<div style="color:#cbd5e1;font-size:0.88rem;margin-top:4px">{plan.communication_topology or "—"}</div></div>'
        f'<div class="ag-stat"><div class="ag-stat-label">Orchestration</div>'
        f'<div style="color:#cbd5e1;font-size:0.88rem;margin-top:4px">{plan.orchestration_pattern or "—"}</div></div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── Agent Decomposition ───────────────────────────────────────────────────
    _section("Agent Decomposition")
    if plan.agent_decomposition:
        for agent in plan.agent_decomposition:
            name           = getattr(agent, "name", str(agent))
            responsibilities = getattr(agent, "responsibilities", [])
            tools          = getattr(agent, "tools", [])

            resp_html = "".join(f'<div style="color:#64748b;font-size:0.83rem;padding:2px 0">• {r}</div>' for r in responsibilities)
            tools_html = " ".join(f'<span class="ag-tag" style="font-family:monospace">{t}</span>' for t in tools) if tools else ""

            st.markdown(
                f'<div class="ag-agent">'
                f'<div style="font-weight:700;color:#f1f5f9;margin-bottom:6px">{name}</div>'
                f'<div style="font-size:0.78rem;color:#475569;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px">Responsibilities</div>'
                f"{resp_html}"
                + (f'<div style="font-size:0.78rem;color:#475569;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin:8px 0 4px">Tools</div>'
                   f'<div class="ag-tag-row">{tools_html}</div>' if tools else "")
                + "</div>",
                unsafe_allow_html=True,
            )

    # ── Migration Phases ──────────────────────────────────────────────────────
    _section("Migration Roadmap")
    if plan.migration_phases:
        for phase in plan.migration_phases:
            phase_num = getattr(phase, "phase", "?")
            name      = getattr(phase, "name", "") or ""
            desc      = getattr(phase, "description", "") or ""
            tasks     = getattr(phase, "tasks", [])
            risks     = getattr(phase, "risks", [])

            tasks_html = "".join(f'<div style="color:#94a3b8;font-size:0.85rem;padding:2px 0">✓ {t}</div>' for t in tasks)
            risks_html = "".join(
                f'<div style="color:#fbbf24;font-size:0.83rem;padding:2px 0">⚠ {r}</div>'
                for r in risks
            ) if risks else ""

            st.markdown(
                f'<div class="ag-phase">'
                f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">'
                f'<span style="background:#6366f1;color:#fff;font-size:0.7rem;font-weight:700;'
                f'padding:2px 8px;border-radius:999px;">Phase {phase_num}</span>'
                f'<span style="font-weight:700;color:#f1f5f9">{name}</span>'
                f"</div>"
                + (f'<div style="color:#64748b;font-size:0.84rem;margin-bottom:8px">{desc}</div>' if desc else "")
                + tasks_html
                + (f'<div style="margin-top:8px">{risks_html}</div>' if risks_html else "")
                + "</div>",
                unsafe_allow_html=True,
            )

    # ── Risk Assessment ───────────────────────────────────────────────────────
    if plan.risk_assessment:
        _section("Risk Assessment")
        st.markdown(
            f'<div class="ag-card" style="border-left:3px solid #f59e0b;padding:12px 16px;">'
            f'<div style="color:#cbd5e1;font-size:0.9rem">{plan.risk_assessment}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    # ── API Documentation ─────────────────────────────────────────────────────
    st.markdown('<div style="border-top:1px solid #1e293b;margin:20px 0 14px;"></div>', unsafe_allow_html=True)
    _section("API Documentation")
    api_gen = ApiDocGenerator()
    api_doc = api_gen.generate(analysis)
    if api_doc:
        with st.expander("View API Documentation", expanded=False):
            st.markdown(api_doc)
        col1, _rest = st.columns([2, 6])
        with col1:
            st.download_button("⬇ Download API Docs", api_doc, "api_documentation.md", "text/markdown", use_container_width=True)
    else:
        st.markdown(
            '<div style="color:#475569;font-size:0.87rem;">No API architecture data available for documentation generation.</div>',
            unsafe_allow_html=True,
        )
