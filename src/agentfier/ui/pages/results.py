import streamlit as st
from agentfier.output.spec_generator import SpecGenerator


def render():
    st.header("Analysis Results")

    if "analysis_result" not in st.session_state:
        st.info("No analysis results yet. Go to the Analyze page to run an analysis.")
        return

    analysis = st.session_state.analysis_result
    spec_gen = SpecGenerator()

    # Download buttons
    col1, col2 = st.columns(2)
    with col1:
        yaml_content = spec_gen.to_yaml(analysis)
        st.download_button("Download YAML Spec", yaml_content, "agentfier_spec.yaml", "text/yaml")
    with col2:
        json_content = spec_gen.to_json(analysis)
        st.download_button("Download JSON Spec", json_content, "agentfier_spec.json", "application/json")

    st.divider()

    dimension_tabs = {
        "tech_stack": ("Technology Stack", _render_tech_stack),
        "dependencies": ("Dependencies", _render_dependencies),
        "data_layer": ("Data Layer", _render_data_layer),
        "integrations": ("Integrations", _render_integrations),
        "auth": ("Auth", _render_auth),
        "observability": ("Observability", _render_observability),
        "api_architecture": ("API", _render_api),
        "business_logic": ("Business Logic", _render_business),
        "infrastructure": ("Infrastructure", _render_infra),
        "security": ("Security", _render_security),
        "frontend": ("Frontend", _render_frontend),
        "configuration": ("Configuration", _render_config),
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


def _render_tech_stack(r):
    if r.languages:
        st.subheader("Languages")
        lang_cols = st.columns(min(len(r.languages), 4))
        for i, lang in enumerate(r.languages):
            with lang_cols[i % len(lang_cols)]:
                name = lang.name if hasattr(lang, "name") else lang.get("name", str(lang))
                pct = lang.percentage if hasattr(lang, "percentage") else lang.get("percentage", 0)
                version = lang.version if hasattr(lang, "version") else lang.get("version", "")
                st.metric(name, f"{pct}%", delta=version if version else None)
    if r.frameworks:
        st.subheader("Frameworks")
        for fw in r.frameworks:
            name = fw.name if hasattr(fw, "name") else fw.get("name", str(fw))
            ver = fw.version if hasattr(fw, "version") else fw.get("version", "")
            cat = fw.category if hasattr(fw, "category") else fw.get("category", "")
            st.write(f"- **{name}** {ver} ({cat})")
    if r.build_tools:
        st.subheader("Build Tools")
        st.write(", ".join(r.build_tools))
    if r.runtime_targets:
        st.subheader("Runtime Targets")
        st.write(", ".join(r.runtime_targets))


def _render_dependencies(r):
    if r.direct:
        st.subheader(f"Direct Dependencies ({len(r.direct)})")
        dep_data = []
        for d in r.direct:
            dep_data.append(d.model_dump() if hasattr(d, "model_dump") else d)
        if dep_data:
            st.dataframe(dep_data, use_container_width=True)
    st.metric("Transitive Dependencies", r.transitive_count)
    if r.vulnerabilities:
        st.subheader("Vulnerabilities")
        for v in r.vulnerabilities:
            sev = v.severity if hasattr(v, "severity") else v.get("severity", "unknown")
            pkg = v.package if hasattr(v, "package") else v.get("package", str(v))
            desc = v.description if hasattr(v, "description") else v.get("description", "")
            if sev in ("high", "critical"):
                st.error(f"**{pkg}** ({sev}): {desc}")
            else:
                st.warning(f"**{pkg}** ({sev}): {desc}")


def _render_data_layer(r):
    if r.databases:
        st.subheader("Databases")
        for db in r.databases:
            t = db.type if hasattr(db, "type") else db.get("type", "")
            n = db.name if hasattr(db, "name") else db.get("name", "")
            p = db.purpose if hasattr(db, "purpose") else db.get("purpose", "")
            st.write(f"- **{t}** - {n} ({p})")
    if r.orms:
        st.subheader("ORM Frameworks")
        st.write(", ".join(r.orms))
    if r.cache_layers:
        st.subheader("Cache Layers")
        for c in r.cache_layers:
            t = c.type if hasattr(c, "type") else c.get("type", "")
            p = c.purpose if hasattr(c, "purpose") else c.get("purpose", "")
            st.write(f"- {t} - {p}")
    if r.message_queues:
        st.subheader("Message Queues")
        for q in r.message_queues:
            t = q.type if hasattr(q, "type") else q.get("type", "")
            p = q.purpose if hasattr(q, "purpose") else q.get("purpose", "")
            st.write(f"- {t} - {p}")
    st.metric("Has Migrations", "Yes" if r.has_migrations else "No")


def _render_integrations(r):
    if r.external_apis:
        st.subheader("External APIs")
        for api in r.external_apis:
            n = api.name if hasattr(api, "name") else api.get("name", "")
            proto = api.protocol if hasattr(api, "protocol") else api.get("protocol", "")
            p = api.purpose if hasattr(api, "purpose") else api.get("purpose", "")
            st.write(f"- **{n}** ({proto}) - {p}")
    if r.third_party_services:
        st.subheader("Third-Party Services")
        for svc in r.third_party_services:
            n = svc.name if hasattr(svc, "name") else svc.get("name", "")
            c = svc.category if hasattr(svc, "category") else svc.get("category", "")
            st.write(f"- **{n}** ({c})")
    if r.message_brokers:
        st.subheader("Message Brokers")
        for mb in r.message_brokers:
            t = mb.type if hasattr(mb, "type") else mb.get("type", "")
            topics = mb.topics if hasattr(mb, "topics") else mb.get("topics", [])
            st.write(f"- {t} - Topics: {', '.join(topics)}")


def _render_auth(r):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Authentication")
        st.write(f"**Methods:** {', '.join(r.methods)}")
        st.write(f"**Token Management:** {r.token_management}")
        if r.identity_providers:
            st.write(f"**Identity Providers:** {', '.join(r.identity_providers)}")
    with col2:
        st.subheader("Authorization")
        st.write(f"**Pattern:** {r.authorization_pattern}")
        st.write(f"**Permission Model:** {r.permission_model}")
        st.metric("Multi-Tenant", "Yes" if r.multi_tenant else "No")


def _render_observability(r):
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Logging Framework:** {r.logging_framework}")
        st.write(f"**Log Format:** {r.log_format}")
        st.metric("Health Checks", "Yes" if r.health_checks else "No")
    with col2:
        if r.metrics_tools:
            st.write(f"**Metrics:** {', '.join(r.metrics_tools)}")
        if r.tracing_tools:
            st.write(f"**Tracing:** {', '.join(r.tracing_tools)}")
        if r.error_tracking:
            st.write(f"**Error Tracking:** {', '.join(r.error_tracking)}")


def _render_api(r):
    st.metric("Total Endpoints", r.total_endpoints)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Style:** {r.api_style}")
    with col2:
        st.write(f"**Versioning:** {r.versioning_strategy}")
    with col3:
        st.metric("Rate Limiting", "Yes" if r.rate_limiting else "No")
    if r.endpoints:
        st.subheader("Endpoints")
        ep_data = []
        for ep in r.endpoints:
            ep_data.append(ep.model_dump() if hasattr(ep, "model_dump") else ep)
        if ep_data:
            st.dataframe(ep_data, use_container_width=True)


def _render_business(r):
    if r.domain_models:
        st.subheader("Domain Models")
        for dm in r.domain_models:
            n = dm.name if hasattr(dm, "name") else dm.get("name", "")
            d = dm.description if hasattr(dm, "description") else dm.get("description", "")
            st.write(f"- **{n}**: {d}")
    if r.workflows:
        st.subheader("Workflows")
        for wf in r.workflows:
            n = wf.name if hasattr(wf, "name") else wf.get("name", "Workflow")
            d = wf.description if hasattr(wf, "description") else wf.get("description", "")
            steps = wf.steps if hasattr(wf, "steps") else wf.get("steps", [])
            with st.expander(n):
                st.write(d)
                for step in steps:
                    st.write(f"  - {step}")
    if r.background_jobs:
        st.subheader("Background Jobs")
        for job in r.background_jobs:
            n = job.name if hasattr(job, "name") else job.get("name", "")
            s = job.schedule if hasattr(job, "schedule") else job.get("schedule", "")
            p = job.purpose if hasattr(job, "purpose") else job.get("purpose", "")
            st.write(f"- **{n}** ({s}) - {p}")


def _render_infra(r):
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Containerized", "Yes" if r.containerized else "No")
        st.write(f"**Orchestration:** {r.orchestration}")
        st.write(f"**Scaling:** {r.scaling_strategy}")
    with col2:
        if r.ci_cd_tools:
            st.write(f"**CI/CD:** {', '.join(r.ci_cd_tools)}")
        if r.iac_tools:
            st.write(f"**IaC:** {', '.join(r.iac_tools)}")
        st.write(f"**Secrets:** {r.secrets_management}")
    if r.environments:
        st.write(f"**Environments:** {', '.join(r.environments)}")


def _render_security(r):
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Encryption at Rest", "Yes" if r.encryption_at_rest else "No")
        st.metric("Encryption in Transit", "Yes" if r.encryption_in_transit else "No")
        st.metric("CORS Configured", "Yes" if r.cors_configured else "No")
    with col2:
        st.metric("Audit Logging", "Yes" if r.audit_logging else "No")
        st.write(f"**Input Validation:** {r.input_validation}")
    if r.compliance_standards:
        st.subheader("Compliance Standards")
        st.write(", ".join(r.compliance_standards))
    if r.security_headers:
        st.subheader("Security Headers")
        st.write(", ".join(r.security_headers))


def _render_frontend(r):
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Framework:** {r.framework} {r.version}")
        st.write(f"**State Management:** {r.state_management}")
        st.write(f"**Routing:** {r.routing_library}")
    with col2:
        st.write(f"**Component Library:** {r.component_library}")
        st.write(f"**Build Tool:** {r.build_tool}")
        st.metric("SSR", "Yes" if r.has_ssr else "No")


def _render_config(r):
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Environment Variables", r.env_vars_count)
        st.write(f"**Config Formats:** {', '.join(r.config_formats)}")
        st.write(f"**Feature Flags:** {r.feature_flags}")
    with col2:
        st.write(f"**Multi-Env Strategy:** {r.multi_env_strategy}")
        st.write(f"**Secrets Approach:** {r.secrets_approach}")
        st.metric("Dynamic Config", "Yes" if r.dynamic_config else "No")
