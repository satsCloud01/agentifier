import streamlit as st
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agentfier.ui.pages import analyze, results, diagrams, conversion, guide

st.set_page_config(
    page_title="Agentfier — Codebase Analyzer",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _inject_css():
    st.markdown(
        """
<style>
/* ─── Base ─────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #020617;
    color: #f1f5f9;
}
[data-testid="stSidebar"] {
    background-color: #0a1120;
    border-right: 1px solid #1e293b;
}
[data-testid="stHeader"] { background: transparent; }

/* ─── Typography ────────────────────────────────────────── */
h1 { color: #f1f5f9; font-size: 1.5rem !important; font-weight: 700 !important; }
h2 { color: #e2e8f0; font-size: 1.15rem !important; font-weight: 600 !important; }
h3 { color: #cbd5e1; font-size: 1rem !important; font-weight: 600 !important; }
p, li { color: #94a3b8; }
strong { color: #e2e8f0 !important; }

/* ─── Sidebar nav radio ─────────────────────────────────── */
[data-testid="stSidebar"] .stRadio > label {
    color: #94a3b8 !important;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.07em;
    text-transform: uppercase;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    color: #cbd5e1 !important;
    font-size: 0.9rem;
    font-weight: 500;
    text-transform: none;
    letter-spacing: normal;
    padding: 6px 10px;
    border-radius: 6px;
    transition: background 0.15s;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
    background: #1e293b;
}

/* ─── Buttons ───────────────────────────────────────────── */
.stButton > button {
    background: #1e293b;
    color: #cbd5e1;
    border: 1px solid #334155;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 500;
    transition: all 0.15s;
}
.stButton > button:hover { background: #273548; border-color: #475569; color: #f1f5f9; }
.stButton > button[kind="primary"] {
    background: #6366f1 !important;
    border-color: #6366f1 !important;
    color: #fff !important;
}
.stButton > button[kind="primary"]:hover { background: #4f46e5 !important; }

/* ─── Download buttons ──────────────────────────────────── */
.stDownloadButton > button {
    background: #1e293b;
    color: #818cf8;
    border: 1px solid #334155;
    border-radius: 8px;
    font-size: 0.83rem;
}
.stDownloadButton > button:hover { background: #273548; color: #a5b4fc; }

/* ─── Metrics ───────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 14px 18px !important;
}
[data-testid="stMetricLabel"] { color: #64748b !important; font-size: 0.75rem !important; }
[data-testid="stMetricValue"] { color: #f1f5f9 !important; font-size: 1.6rem !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"] { font-size: 0.78rem !important; }

/* ─── Tabs ──────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #0f172a;
    border-bottom: 1px solid #1e293b;
    border-radius: 10px 10px 0 0;
    padding: 4px 8px 0;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    color: #64748b;
    font-size: 0.82rem;
    font-weight: 500;
    border-radius: 8px 8px 0 0;
    padding: 8px 14px;
    border: none !important;
    background: transparent;
}
.stTabs [aria-selected="true"] {
    color: #818cf8 !important;
    background: #1e293b !important;
    border-bottom: 2px solid #6366f1 !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-top: none;
    border-radius: 0 0 10px 10px;
    padding: 20px !important;
}

/* ─── Expanders ─────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
    margin-bottom: 8px;
}
[data-testid="stExpander"] summary {
    color: #cbd5e1;
    font-weight: 600;
    font-size: 0.9rem;
    padding: 12px 16px;
}
[data-testid="stExpander"] summary:hover { background: #1e293b; border-radius: 10px; }

/* ─── DataFrames ────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid #1e293b;
    border-radius: 8px;
    overflow: hidden;
}

/* ─── Alerts / Info boxes ───────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 8px;
    border-left-width: 3px;
}
.stAlert[data-baseweb="notification"][kind="info"] { background: #0c1a36 !important; border-color: #3b82f6 !important; }
.stAlert[data-baseweb="notification"][kind="warning"] { background: #1c1203 !important; border-color: #f59e0b !important; }
.stAlert[data-baseweb="notification"][kind="error"] { background: #1c0606 !important; border-color: #ef4444 !important; }

/* ─── Progress bar ──────────────────────────────────────── */
.stProgress > div > div > div { background: #6366f1; border-radius: 999px; }
.stProgress > div > div { background: #1e293b; border-radius: 999px; }

/* ─── Divider ───────────────────────────────────────────── */
hr { border-color: #1e293b !important; }

/* ─── Text inputs ───────────────────────────────────────── */
.stTextInput input, .stTextArea textarea {
    background: #0f172a !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    color: #f1f5f9 !important;
}
.stTextInput input:focus, .stTextArea textarea:focus { border-color: #6366f1 !important; box-shadow: 0 0 0 2px rgba(99,102,241,0.2) !important; }

/* ─── Selectbox ─────────────────────────────────────────── */
.stSelectbox div[data-baseweb="select"] > div {
    background: #0f172a !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    color: #f1f5f9 !important;
}

/* ─── Checkboxes ────────────────────────────────────────── */
.stCheckbox label { color: #cbd5e1 !important; font-size: 0.88rem; }

/* ─── Slider ────────────────────────────────────────────── */
.stSlider [data-testid="stThumbValue"] { color: #818cf8 !important; }

/* ─── File uploader ─────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: #0f172a;
    border: 1px dashed #334155;
    border-radius: 10px;
}

/* ─── Code blocks ───────────────────────────────────────── */
.stCode, pre {
    background: #0a1120 !important;
    border: 1px solid #1e293b;
    border-radius: 8px;
}

/* ─── Status widget ─────────────────────────────────────── */
[data-testid="stStatusWidget"] {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 8px;
}

/* ─── Scrollbar ─────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #475569; }

/* ─── Sidebar version caption ───────────────────────────── */
[data-testid="stSidebar"] .stCaption { color: #334155 !important; }

/* ─── Card utility (use via st.markdown unsafe_allow_html) ─ */
.ag-card {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 12px;
}
.ag-card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.82rem;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 12px;
}
.ag-badge {
    display: inline-flex;
    align-items: center;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 500;
    background: #1e293b;
    color: #94a3b8;
    border: 1px solid #334155;
}
.ag-badge-indigo { background: rgba(99,102,241,0.15); color: #818cf8; border-color: rgba(99,102,241,0.3); }
.ag-badge-green  { background: rgba(16,185,129,0.12); color: #34d399; border-color: rgba(16,185,129,0.25); }
.ag-badge-yellow { background: rgba(245,158,11,0.12); color: #fbbf24; border-color: rgba(245,158,11,0.25); }
.ag-badge-red    { background: rgba(239,68,68,0.12);  color: #f87171; border-color: rgba(239,68,68,0.25); }
.ag-stat-row { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
.ag-stat {
    flex: 1 1 140px;
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 14px 16px;
}
.ag-stat-label { font-size: 0.72rem; color: #475569; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px; }
.ag-stat-value { font-size: 1.5rem; font-weight: 700; color: #f1f5f9; }
.ag-stat-sub   { font-size: 0.72rem; color: #64748b; margin-top: 2px; }
.ag-section-title {
    font-size: 0.78rem;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin: 20px 0 8px;
    padding-bottom: 6px;
    border-bottom: 1px solid #1e293b;
}
.ag-page-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #f1f5f9;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 4px;
}
.ag-page-sub { font-size: 0.82rem; color: #475569; margin-bottom: 20px; }
.ag-icon { color: #818cf8; }
.ag-tag-row { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
.ag-tag {
    background: #1e293b;
    color: #94a3b8;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 0.78rem;
}
.ag-bullet {
    color: #94a3b8;
    font-size: 0.87rem;
    padding: 4px 0 4px 16px;
    border-left: 2px solid #1e293b;
    margin-bottom: 4px;
}
.ag-phase {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-left: 3px solid #6366f1;
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.ag-agent {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-left: 3px solid #10b981;
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    margin-bottom: 10px;
}
</style>
""",
        unsafe_allow_html=True,
    )


def _inject_light_css():
    """Override dark theme with light colors when user toggles to light mode."""
    st.markdown("""<style>
html, body, [data-testid="stAppViewContainer"] {
    background-color: #f8fafc !important; color: #1e293b !important;
}
[data-testid="stSidebar"] {
    background-color: #ffffff !important; border-right: 1px solid #e2e8f0 !important;
}
[data-testid="stHeader"] { background: rgba(248,250,252,0.8) !important; }
h1 { color: #1e293b !important; } h2 { color: #334155 !important; } h3 { color: #475569 !important; }
p, li { color: #475569 !important; } strong { color: #1e293b !important; }
[data-testid="stSidebar"] .stRadio > label { color: #64748b !important; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label { color: #334155 !important; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover { background: #f1f5f9 !important; }
.stButton > button { background: #f1f5f9 !important; color: #334155 !important; border: 1px solid #e2e8f0 !important; }
.stButton > button:hover { background: #e2e8f0 !important; color: #1e293b !important; }
.stButton > button[kind="primary"] { background: #6366f1 !important; color: #fff !important; }
[data-testid="stMetric"] { background: #ffffff !important; border: 1px solid #e2e8f0 !important; }
[data-testid="stMetricLabel"] { color: #64748b !important; }
[data-testid="stMetricValue"] { color: #1e293b !important; }
.stTabs [data-baseweb="tab-list"] { background: #ffffff !important; border-bottom-color: #e2e8f0 !important; }
.stTabs [data-baseweb="tab"] { color: #64748b !important; }
.stTabs [aria-selected="true"] { color: #6366f1 !important; background: #f1f5f9 !important; }
.stTabs [data-baseweb="tab-panel"] { background: #ffffff !important; border-color: #e2e8f0 !important; }
[data-testid="stExpander"] { background: #ffffff !important; border-color: #e2e8f0 !important; }
[data-testid="stExpander"] summary { color: #334155 !important; }
[data-testid="stExpander"] summary:hover { background: #f1f5f9 !important; }
.stTextInput input, .stTextArea textarea { background: #ffffff !important; border-color: #e2e8f0 !important; color: #1e293b !important; }
.stSelectbox div[data-baseweb="select"] > div { background: #ffffff !important; border-color: #e2e8f0 !important; color: #1e293b !important; }
.stCheckbox label { color: #334155 !important; }
[data-testid="stFileUploader"] { background: #ffffff !important; border-color: #e2e8f0 !important; }
.stCode, pre { background: #f8fafc !important; border-color: #e2e8f0 !important; }
hr { border-color: #e2e8f0 !important; }
.ag-card { background: #ffffff !important; border-color: #e2e8f0 !important; }
.ag-card-header { color: #64748b !important; }
.ag-badge { background: #f1f5f9 !important; color: #475569 !important; border-color: #e2e8f0 !important; }
.ag-stat { background: #ffffff !important; border-color: #e2e8f0 !important; }
.ag-stat-label { color: #64748b !important; }
.ag-stat-value { color: #1e293b !important; }
.ag-stat-sub { color: #64748b !important; }
.ag-section-title { color: #64748b !important; border-bottom-color: #e2e8f0 !important; }
.ag-page-title { color: #1e293b !important; }
[data-testid="stSidebar"] .stCaption { color: #94a3b8 !important; }
</style>""", unsafe_allow_html=True)


def main():
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"

    _inject_css()
    if st.session_state.theme == "light":
        _inject_light_css()

    # Sidebar
    with st.sidebar:
        st.markdown(
            """
<div style="padding: 4px 0 16px">
  <div style="font-size:1.15rem;font-weight:700;color:#f1f5f9;display:flex;align-items:center;gap:8px;">
    <span style="color:#6366f1;font-size:1.3rem;">⬡</span> Agentfier
  </div>
  <div style="font-size:0.75rem;color:#475569;margin-top:2px;">Codebase → Agent-Native</div>
</div>
""",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="border-top:1px solid #1e293b;margin-bottom:12px;"></div>',
            unsafe_allow_html=True,
        )

        page = st.radio(
            "Navigation",
            ["⬡ Tour", "Analyze", "Results", "Diagrams", "Conversion Plan"],
            index=0,
            label_visibility="collapsed",
        )

        st.markdown(
            '<div style="border-top:1px solid #1e293b;margin:12px 0;"></div>',
            unsafe_allow_html=True,
        )

        # ── API Key (always visible, session-only — never read from env) ──────
        st.markdown(
            '<div style="font-size:0.72rem;font-weight:600;color:#475569;'
            'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;">🔑 API Key</div>',
            unsafe_allow_html=True,
        )
        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            value=st.session_state.get("api_key", ""),
            placeholder="sk-ant-… (session only, never stored)",
            label_visibility="collapsed",
        )
        if api_key:
            st.session_state.api_key = api_key
        elif "api_key" in st.session_state and not api_key:
            # User cleared the field — remove from session
            del st.session_state.api_key

        if st.session_state.get("api_key"):
            st.markdown(
                '<div style="font-size:0.75rem;color:#34d399;margin-bottom:8px;">✓ Key set for this session</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="font-size:0.75rem;color:#f59e0b;margin-bottom:8px;">⚠ Required for AI features</div>',
                unsafe_allow_html=True,
            )

        with st.expander("⚙ Model & Limits", expanded=False):
            model = st.selectbox(
                "Model",
                [
                    "claude-sonnet-4-6",
                    "claude-opus-4-6",
                    "claude-haiku-4-5-20251001",
                ],
            )
            max_files = st.slider("Max Files to Analyze", 50, 1000, 500, step=50)
            st.session_state.model = model
            st.session_state.max_files = max_files

        st.markdown(
            '<div style="border-top:1px solid #1e293b;margin:12px 0;"></div>',
            unsafe_allow_html=True,
        )

        theme_label = "☀️ Light Mode" if st.session_state.theme == "dark" else "🌙 Dark Mode"
        if st.button(theme_label, key="theme_toggle", use_container_width=True):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()

        st.caption("Agentfier v0.1.0")
        st.markdown(
            "Developed by **Sathish Siva Shankar**  \n"
            "[View All Solutions →](https://my-solution-registry.satszone.link)",
        )

    # Route to selected page
    if page == "⬡ Tour":
        guide.render()
    elif page == "Analyze":
        analyze.render()
    elif page == "Results":
        results.render()
    elif page == "Diagrams":
        diagrams.render()
    elif page == "Conversion Plan":
        conversion.render()


if __name__ == "__main__":
    main()
