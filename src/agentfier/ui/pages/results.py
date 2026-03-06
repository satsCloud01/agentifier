import streamlit as st
from agentfier.output.spec_generator import SpecGenerator


# ── Helpers ──────────────────────────────────────────────────────────────────

def _badge(label: str, variant: str = "") -> str:
    cls = f"ag-badge {f'ag-badge-{variant}' if variant else ''}"
    return f'<span class="{cls}">{label}</span>'


def _section(title: str) -> None:
    st.markdown(f'<div class="ag-section-title">{title}</div>', unsafe_allow_html=True)


def _tags(items: list) -> None:
    if not items:
        return
    tags = " ".join(f'<span class="ag-tag">{t}</span>' for t in items)
    st.markdown(f'<div class="ag-tag-row">{tags}</div>', unsafe_allow_html=True)


def _bullet(text: str) -> None:
    st.markdown(f'<div class="ag-bullet">{text}</div>', unsafe_allow_html=True)


def _attr(obj, *keys):
    for k in keys:
        v = getattr(obj, k, None) if not isinstance(obj, dict) else obj.get(k)
        if v is not None:
            return v
    return ""


# ── Page ─────────────────────────────────────────────────────────────────────

def render():
    st.markdown(
        """
<div class="ag-page-title">
  <span class="ag-icon">📊</span> Analysis Results
</div>
<div class="ag-page-sub">Browse results across 12 architectural dimensions. Download the full spec as YAML or JSON.</div>
""",
        unsafe_allow_html=True,
    )

    if "analysis_result" not in st.session_state:
        st.info("No analysis results yet. Go to the **Analyze** page to run an analysis.")
        return

    analysis = st.session_state.analysis_result
    spec_gen = SpecGenerator()

    # ── Download row ──────────────────────────────────────────────────────────
    col1, col2, _rest = st.columns([1, 1, 6])
    with col1:
        yaml_content = spec_gen.to_yaml(analysis)
        st.download_button("⬇ YAML Spec", yaml_content, "agentfier_spec.yaml", "text/yaml", use_container_width=True)
    with col2:
        json_content = spec_gen.to_json(analysis)
        st.download_button("⬇ JSON Spec", json_content, "agentfier_spec.json", "application/json", use_container_width=True)

    st.markdown('<div style="border-top:1px solid #1e293b;margin:14px 0;"></div>', unsafe_allow_html=True)

    # ── Summary stat row ──────────────────────────────────────────────────────
    dims_done = sum(
        1 for d in [
            "tech_stack", "dependencies", "data_layer", "integrations", "auth",
            "observability", "api_architecture", "business_logic", "infrastructure",
            "security", "frontend", "configuration",
        ]
        if getattr(analysis, d, None) is not None
    )
    api_count  = analysis.api_architecture.total_endpoints if analysis.api_architecture else 0
    vuln_count = len(analysis.dependencies.vulnerabilities) if analysis.dependencies else 0
    lang_count = len(analysis.tech_stack.languages) if analysis.tech_stack else 0

    st.markdown(
        f"""
<div class="ag-stat-row">
  <div class="ag-stat">
    <div class="ag-stat-label">Dimensions</div>
    <div class="ag-stat-value">{dims_done}</div>
    <div class="ag-stat-sub">of 12 analyzed</div>
  </div>
  <div class="ag-stat">
    <div class="ag-stat-label">Languages</div>
    <div class="ag-stat-value">{lang_count}</div>
    <div class="ag-stat-sub">detected</div>
  </div>
  <div class="ag-stat">
    <div class="ag-stat-label">API Endpoints</div>
    <div class="ag-stat-value">{api_count}</div>
    <div class="ag-stat-sub">discovered</div>
  </div>
  <div class="ag-stat">
    <div class="ag-stat-label">Vulnerabilities</div>
    <div class="ag-stat-value" style="color:{'#f87171' if vuln_count > 0 else '#34d399'}">{vuln_count}</div>
    <div class="ag-stat-sub">{'requires attention' if vuln_count > 0 else 'none found'}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # ── Dimension tabs ────────────────────────────────────────────────────────
    dimension_tabs = {
        "tech_stack":       ("⬡ Tech Stack",       _render_tech_stack),
        "dependencies":     ("📦 Dependencies",     _render_dependencies),
        "data_layer":       ("🗄 Data Layer",       _render_data_layer),
        "integrations":     ("🔌 Integrations",     _render_integrations),
        "auth":             ("🔑 Auth",             _render_auth),
        "observability":    ("📈 Observability",    _render_observability),
        "api_architecture": ("🔗 API",              _render_api),
        "business_logic":   ("⚙ Business Logic",   _render_business),
        "infrastructure":   ("🏗 Infrastructure",   _render_infra),
        "security":         ("🛡 Security",         _render_security),
        "frontend":         ("🖥 Frontend",         _render_frontend),
        "configuration":    ("⚡ Configuration",    _render_config),
    }

    available = [
        (key, name, fn)
        for key, (name, fn) in dimension_tabs.items()
        if getattr(analysis, key, None) is not None
    ]

    if not available:
        st.warning("No dimension results available.")
        return

    tab_names = [name for _, name, _ in available]
    tabs = st.tabs(tab_names)

    for tab, (key, _name, render_fn) in zip(tabs, available):
        with tab:
            render_fn(getattr(analysis, key))


# ── Dimension renderers ───────────────────────────────────────────────────────

def _render_tech_stack(r):
    if r.languages:
        _section("Languages")
        lang_cols = st.columns(min(len(r.languages), 4))
        for i, lang in enumerate(r.languages):
            name = _attr(lang, "name")
            pct  = _attr(lang, "percentage") or 0
            ver  = _attr(lang, "version") or ""
            with lang_cols[i % len(lang_cols)]:
                st.metric(name, f"{pct}%", delta=ver if ver else None)

    if r.frameworks:
        _section("Frameworks")
        html = ""
        for fw in r.frameworks:
            name = _attr(fw, "name"); ver = _attr(fw, "version") or ""; cat = _attr(fw, "category") or ""
            ver_html = f' <span style="color:#475569">v{ver}</span>' if ver else ""
            cat_html = f" {_badge(cat, 'indigo')}" if cat else ""
            html += (
                f'<div class="ag-card" style="padding:10px 14px;margin-bottom:6px;">'
                f'<strong style="color:#f1f5f9">{name}</strong>'
                f"{ver_html}{cat_html}"
                f"</div>"
            )
        st.markdown(html, unsafe_allow_html=True)

    if r.build_tools:
        _section("Build Tools"); _tags(r.build_tools)
    if r.runtime_targets:
        _section("Runtime Targets"); _tags(r.runtime_targets)
    if r.confidence:
        conf_pct = int(r.confidence * 100)
        variant = "green" if conf_pct >= 80 else "yellow" if conf_pct >= 50 else "red"
        st.markdown(f'<div style="margin-top:12px;">{_badge(f"Confidence: {conf_pct}%", variant)}</div>', unsafe_allow_html=True)


def _render_dependencies(r):
    col1, col2 = st.columns(2)
    with col1: st.metric("Direct Dependencies", len(r.direct))
    with col2: st.metric("Transitive Count", r.transitive_count)

    if r.vulnerabilities:
        _section("Vulnerabilities")
        for v in r.vulnerabilities:
            sev  = _attr(v, "severity") or "unknown"
            pkg  = _attr(v, "package") or str(v)
            desc = _attr(v, "description") or ""
            color = "#ef4444" if sev in ("high", "critical") else "#f59e0b"
            variant = "red" if sev in ("high", "critical") else "yellow"
            st.markdown(
                f'<div class="ag-card" style="border-left:3px solid {color};padding:10px 14px;margin-bottom:6px;">'
                f'{_badge(sev.upper(), variant)} <strong style="color:#f1f5f9;margin-left:6px">{pkg}</strong>'
                f'<div style="color:#64748b;font-size:0.82rem;margin-top:4px">{desc}</div></div>',
                unsafe_allow_html=True,
            )

    if r.direct:
        _section("Direct Dependencies")
        dep_data = [d.model_dump() if hasattr(d, "model_dump") else d for d in r.direct]
        st.dataframe(dep_data, use_container_width=True)

    if r.licenses:
        _section("License Groups")
        for lic, pkgs in r.licenses.items():
            _bullet(f"<strong>{lic}</strong>: {', '.join(pkgs)}")


def _render_data_layer(r):
    col1, col2 = st.columns(2)
    with col1:
        if r.databases:
            _section("Databases")
            for db in r.databases:
                t = _attr(db, "type"); n = _attr(db, "name"); p = _attr(db, "purpose")
                st.markdown(
                    f'<div class="ag-card" style="padding:10px 14px;margin-bottom:6px;">'
                    f'{_badge(t, "indigo")} <strong style="color:#f1f5f9;margin-left:6px">{n}</strong>'
                    f'<div style="color:#64748b;font-size:0.82rem">{p}</div></div>',
                    unsafe_allow_html=True,
                )
        if r.orms:
            _section("ORM Frameworks"); _tags(r.orms)
    with col2:
        if r.cache_layers:
            _section("Cache Layers")
            for c in r.cache_layers:
                _bullet(f"<strong>{_attr(c, 'type')}</strong> — {_attr(c, 'purpose')}")
        if r.message_queues:
            _section("Message Queues")
            for q in r.message_queues:
                _bullet(f"<strong>{_attr(q, 'type')}</strong> — {_attr(q, 'purpose')}")
    st.markdown(
        f'<div style="margin-top:10px;">{_badge("Has Migrations ✓", "green") if r.has_migrations else _badge("No Migrations")}</div>',
        unsafe_allow_html=True,
    )


def _render_integrations(r):
    if r.external_apis:
        _section("External APIs")
        for api in r.external_apis:
            n = _attr(api, "name"); proto = _attr(api, "protocol"); p = _attr(api, "purpose"); auth = _attr(api, "auth_method")
            proto_html = f" {_badge(proto, 'indigo')}" if proto else ""
            auth_html = f" · Auth: {auth}" if auth else ""
            st.markdown(
                f'<div class="ag-card" style="padding:10px 14px;margin-bottom:6px;">'
                f'<strong style="color:#f1f5f9">{n}</strong>{proto_html}'
                f'<div style="color:#64748b;font-size:0.82rem;margin-top:3px">{p}{auth_html}</div></div>',
                unsafe_allow_html=True,
            )
    if r.third_party_services:
        _section("Third-Party Services")
        parts = []
        for s in r.third_party_services:
            sname = _attr(s, "name")
            scat = _attr(s, "category")
            cat_suffix = f" ({scat})" if scat else ""
            parts.append(f'<span class="ag-tag">{sname}{cat_suffix}</span>')
        html = "".join(parts)
        st.markdown(f'<div class="ag-tag-row">{html}</div>', unsafe_allow_html=True)
    if r.webhooks:
        _section("Webhooks"); _tags(r.webhooks)
    if r.message_brokers:
        _section("Message Brokers")
        for mb in r.message_brokers:
            t = _attr(mb, "type"); topics = _attr(mb, "topics") or []
            st.markdown(
                f'<div class="ag-card" style="padding:10px 14px;margin-bottom:6px;">'
                f'<strong style="color:#f1f5f9">{t}</strong>'
                f'<div style="margin-top:5px">'
                + " ".join(f'<span class="ag-tag">{tp}</span>' for tp in topics)
                + "</div></div>",
                unsafe_allow_html=True,
            )


def _render_auth(r):
    col1, col2 = st.columns(2)
    with col1:
        _section("Authentication"); _tags(r.methods)
        if r.token_management:
            _bullet(f"Token: <strong>{r.token_management}</strong>")
        if r.identity_providers:
            _section("Identity Providers"); _tags(r.identity_providers)
    with col2:
        _section("Authorization")
        st.markdown(
            f'<div class="ag-card" style="padding:12px 16px;">'
            f'<div style="font-size:0.8rem;color:#64748b">Pattern</div>'
            f'<div style="font-size:1.05rem;font-weight:600;color:#f1f5f9">{r.authorization_pattern or "—"}</div>'
            f'<div style="font-size:0.8rem;color:#64748b;margin-top:8px">Permission Model</div>'
            f'<div style="color:#cbd5e1;font-size:0.9rem">{r.permission_model or "—"}</div>'
            f'<div style="margin-top:10px">'
            f'{_badge("Multi-tenant", "indigo") if r.multi_tenant else _badge("Single-tenant")}'
            f"</div></div>",
            unsafe_allow_html=True,
        )


def _render_observability(r):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f'<div class="ag-card" style="padding:12px 16px;">'
            f'<div style="font-size:0.78rem;color:#64748b">Logging Framework</div>'
            f'<div style="color:#f1f5f9;font-weight:600">{r.logging_framework or "—"}</div>'
            f'<div style="font-size:0.78rem;color:#64748b;margin-top:8px">Log Format</div>'
            f'<div style="color:#cbd5e1">{r.log_format or "—"}</div>'
            f'<div style="margin-top:10px">'
            f'{_badge("Health Checks ✓", "green") if r.health_checks else _badge("No Health Checks")}'
            f"</div></div>",
            unsafe_allow_html=True,
        )
    with col2:
        if r.metrics_tools:
            _section("Metrics"); _tags(r.metrics_tools)
        if r.tracing_tools:
            _section("Tracing"); _tags(r.tracing_tools)
        if r.apm_tools:
            _section("APM"); _tags(r.apm_tools)
        if r.error_tracking:
            _section("Error Tracking"); _tags(r.error_tracking)


def _render_api(r):
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Endpoints", r.total_endpoints)
    with col2: st.metric("Style", r.api_style or "—")
    with col3: st.metric("Rate Limiting", "Yes" if r.rate_limiting else "No")
    with col4: st.metric("Versioning", r.versioning_strategy or "—")
    if r.endpoints:
        _section("Endpoint List")
        ep_data = [ep.model_dump() if hasattr(ep, "model_dump") else ep for ep in r.endpoints]
        st.dataframe(ep_data, use_container_width=True)
    if r.documentation_format:
        st.markdown(f'<div style="margin-top:10px;">{_badge(f"Docs: {r.documentation_format}", "indigo")}</div>', unsafe_allow_html=True)


def _render_business(r):
    if r.domain_models:
        _section("Domain Models")
        html = "".join(
            f'<div class="ag-card" style="padding:10px 14px;margin-bottom:6px;">'
            f'<strong style="color:#f1f5f9">{_attr(dm, "name")}</strong>'
            f'<div style="color:#64748b;font-size:0.82rem;margin-top:2px">{_attr(dm, "description") or ""}</div></div>'
            for dm in r.domain_models
        )
        st.markdown(html, unsafe_allow_html=True)
    if r.workflows:
        _section("Workflows")
        for wf in r.workflows:
            n = _attr(wf, "name") or "Workflow"; d = _attr(wf, "description") or ""; steps = _attr(wf, "steps") or []
            with st.expander(n, expanded=False):
                if d:
                    st.markdown(f'<div style="color:#64748b;font-size:0.88rem;margin-bottom:8px">{d}</div>', unsafe_allow_html=True)
                for step in steps:
                    _bullet(step)
    if r.background_jobs:
        _section("Background Jobs")
        for job in r.background_jobs:
            n = _attr(job, "name"); s = _attr(job, "schedule") or ""; p = _attr(job, "purpose") or ""
            _bullet(f'<strong>{n}</strong>{f" ({s})" if s else ""} — {p}')
    if r.state_machines:
        _section("State Machines"); _tags(r.state_machines)
    if r.event_patterns:
        _section("Event Patterns"); _tags(r.event_patterns)


def _render_infra(r):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f'<div class="ag-card" style="padding:12px 16px;">'
            f'{_badge("Containerized ✓", "green") if r.containerized else _badge("Not Containerized")}'
            f'<div style="font-size:0.78rem;color:#64748b;margin-top:10px">Orchestration</div>'
            f'<div style="color:#f1f5f9;font-weight:600">{r.orchestration or "—"}</div>'
            f'<div style="font-size:0.78rem;color:#64748b;margin-top:8px">Scaling</div>'
            f'<div style="color:#cbd5e1">{r.scaling_strategy or "—"}</div>'
            f'<div style="font-size:0.78rem;color:#64748b;margin-top:8px">Secrets Management</div>'
            f'<div style="color:#cbd5e1">{r.secrets_management or "—"}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
    with col2:
        if r.ci_cd_tools:
            _section("CI/CD"); _tags(r.ci_cd_tools)
        if r.iac_tools:
            _section("IaC Tools"); _tags(r.iac_tools)
        if r.environments:
            _section("Environments"); _tags(r.environments)


def _render_security(r):
    flags = [
        ("Encryption at Rest",    r.encryption_at_rest),
        ("Encryption in Transit", r.encryption_in_transit),
        ("CORS Configured",       r.cors_configured),
        ("Audit Logging",         r.audit_logging),
    ]
    html = '<div class="ag-stat-row">'
    for label, val in flags:
        color = "#34d399" if val else "#ef4444"
        symbol = "✓" if val else "✗"
        html += (
            f'<div class="ag-stat" style="flex:1 1 120px;border-left:2px solid {color};">'
            f'<div class="ag-stat-label">{label}</div>'
            f'<div style="font-size:1.4rem;color:{color}">{symbol}</div></div>'
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if r.input_validation:
            _section("Input Validation"); _bullet(r.input_validation)
        if r.compliance_standards:
            _section("Compliance Standards"); _tags(r.compliance_standards)
    with col2:
        if r.security_headers:
            _section("Security Headers"); _tags(r.security_headers)


def _render_frontend(r):
    st.markdown(
        f'<div class="ag-card" style="padding:14px 18px;">'
        f'<div class="ag-stat-row" style="margin-bottom:0">'
        f'<div class="ag-stat"><div class="ag-stat-label">Framework</div>'
        f'<div style="font-size:1rem;font-weight:700;color:#f1f5f9">{r.framework or "—"} {r.version or ""}</div></div>'
        f'<div class="ag-stat"><div class="ag-stat-label">State Mgmt</div><div style="color:#cbd5e1">{r.state_management or "—"}</div></div>'
        f'<div class="ag-stat"><div class="ag-stat-label">Routing</div><div style="color:#cbd5e1">{r.routing_library or "—"}</div></div>'
        f'<div class="ag-stat"><div class="ag-stat-label">Components</div><div style="color:#cbd5e1">{r.component_library or "—"}</div></div>'
        f'<div class="ag-stat"><div class="ag-stat-label">Build Tool</div><div style="color:#cbd5e1">{r.build_tool or "—"}</div></div>'
        f'<div class="ag-stat"><div class="ag-stat-label">SSR</div>'
        f'{_badge("Yes ✓", "green") if r.has_ssr else _badge("No")}</div>'
        f"</div></div>",
        unsafe_allow_html=True,
    )


def _render_config(r):
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Environment Variables", r.env_vars_count)
        if r.config_formats:
            _section("Config Formats"); _tags(r.config_formats)
        if r.feature_flags:
            _section("Feature Flags"); _bullet(r.feature_flags)
    with col2:
        if r.multi_env_strategy:
            _section("Multi-Env Strategy"); _bullet(r.multi_env_strategy)
        if r.secrets_approach:
            _section("Secrets Approach"); _bullet(r.secrets_approach)
        st.markdown(
            f'<div style="margin-top:10px;">'
            f'{_badge("Dynamic Config ✓", "green") if r.dynamic_config else _badge("Static Config")}'
            f"</div>",
            unsafe_allow_html=True,
        )
