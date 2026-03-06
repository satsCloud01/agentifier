# Agentfier — Constraints

Technical, design, and operational constraints.

---

## Technical Constraints

### Runtime Environment

| Constraint | Detail |
|-----------|--------|
| **Python ≥ 3.10** | Type union syntax (`X \| Y`), `match` statements |
| **Streamlit ≥ 1.40** | `st.status`, `use_container_width` on download buttons |
| **Pydantic v2** | `model_validate_json`, `model_dump` API (not v1 compatible) |
| **Anthropic SDK ≥ 0.40** | `client.messages.create` interface |
| **Single-process** | Streamlit runs in one Python process; no background workers |

### Optional Dependencies

| Component | Constraint |
|-----------|-----------|
| **Graphviz system package** | Required for SVG/PNG diagram rendering; without it, DOT source is shown |
| **Java 17+** | Required for CFR decompiler (JAR/WAR ingestion); CFR auto-downloads on first use |
| **Git** | Required for GitHub ingestion (via GitPython's `Repo.clone_from`) |

### File / Size Limits

| Limit | Default | Config key |
|-------|---------|-----------|
| Max file size to read | 100 MB | `MAX_FILE_SIZE_MB` |
| Max files per analyzer | 500 | `MAX_FILES_TO_ANALYZE` |
| Skipped directories | `.git`, `node_modules`, `target`, `build`, `dist`, `.venv` | hardcoded in `BaseIngestor._build_manifest` |
| Skipped binary extensions | `.class`, `.jar`, `.war`, `.png`, `.jpg`, `.gif`, `.ico`, `.woff*`, `.ttf`, `.eot`, `.so`, `.dylib`, `.dll`, `.exe` | hardcoded |

---

## Design Constraints

### API Key Policy

- **No persistence**: The Anthropic API key is entered via the UI sidebar and stored only in `st.session_state` for the duration of the browser session.
- **No environment variable fallback**: Pages never call `os.environ.get("ANTHROPIC_API_KEY")`. The key is always sourced from `st.session_state.get("api_key", "")`.
- **No file storage**: The key is never written to `.env`, database, disk, or any other persistent medium.
- **Cleared on browser close**: Streamlit session state is not persisted across server restarts or tab closes.

### Stateless Analysis Pipeline

- Each analysis run is independent; results are stored only in `st.session_state`.
- No database or persistent queue.
- Workspace files (`data/workspaces/`) persist on disk between runs but are not indexed or versioned by the app.

### Claude API Calls

- **Synchronous**: All Claude calls block the Streamlit thread. Long analyses (12 dimensions) may take 3–8 minutes.
- **Retry policy**: Up to 3 attempts per dimension on `JSONDecodeError` or `ValidationError`. The error is fed back to Claude for self-correction.
- **No streaming**: Responses are collected as complete messages (no `stream=True`).
- **Model selection**: Configurable in the sidebar; defaults to `claude-sonnet-4-6`.

### Output Files

- YAML/JSON specs and diagrams are written to `data/outputs/` (configurable via `OUTPUT_DIR` env var).
- Files are not cleaned up automatically; old runs accumulate on disk.
- `data/workspaces/` and `data/outputs/` are in `.gitignore`.

---

## Security Constraints

| Constraint | Detail |
|-----------|--------|
| **No server-side secrets** | No `.env` required at runtime; key provided per session |
| **Local-only by default** | Streamlit binds to `localhost:8501`; requires reverse proxy (nginx) for public exposure |
| **Subprocess execution** | `JarIngestor` spawns `java -jar cfr.jar` subprocess; input is a file path, not user-controlled shell argument |
| **defusedxml** | All XML parsing (Maven POM, Spring XML) uses `defusedxml` to prevent XXE attacks |
| **chardet** | Binary file detection uses `chardet` to avoid reading large binary files as text |
| **No eval / exec** | Analysis code does not dynamically execute any code from the analyzed codebase |

---

## Operational Constraints

### Deployment (AWS EC2 t2.micro)

| Constraint | Detail |
|-----------|--------|
| **RAM** | 1 GB — sufficient for Streamlit + Pydantic; large repos (>5k files) may approach limit |
| **CPU** | 1 vCPU — analysis is single-threaded; concurrent users share one process |
| **Disk** | 8 GB EBS — `data/workspaces/` must be monitored and cleaned periodically |
| **Network** | GitHub clone is outbound; Anthropic API is outbound; no inbound ports except 80/443 |
| **Concurrency** | Single Streamlit server; multiple browser tabs share session state isolation but the same process |

### Nginx Reverse Proxy

- Streamlit requires WebSocket support (`proxy_http_version 1.1`, `Upgrade`, `Connection` headers).
- Max request body size must be increased for JAR/WAR uploads (`client_max_body_size 512m`).

### Streamlit-Specific

- `st.rerun()` causes a full script re-execution; all local variables are reset.
- Session state (`st.session_state`) persists within a session but not across browser tabs.
- `st.status` and `st.tabs` require Streamlit ≥ 1.28.

---

## Known Limitations

1. **Private repositories** require Git credentials pre-configured on the machine (SSH key or HTTPS token in `.gitconfig`).
2. **Obfuscated JARs** produce partial decompilation; Claude will still analyze what CFR can recover.
3. **Very large codebases** (10k+ files) are capped at `MAX_FILES_TO_ANALYZE`; the cap applies per dimension, not globally.
4. **Token limits**: Each dimension call is capped at `MAX_TOKENS` (default 4096). Complex codebases may need this increased.
5. **Rate limits**: Anthropic API rate limits may slow rapid consecutive full-dimension analyses.
6. **No incremental analysis**: Re-running analysis replaces the entire `st.session_state.analysis_result`.
7. **Single tenant**: No user accounts, no multi-user separation; all users share the same Streamlit process and output directory.
