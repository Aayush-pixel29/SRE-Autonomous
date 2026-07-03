import streamlit as st
import requests
import time

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Enterprise SRE Swarm · AI Ops Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Google Font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* Global reset */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Dark background */
.stApp { background: #0a0e1a; }

/* Hide default streamlit header */
#MainMenu, footer, header { visibility: hidden; }

/* ── Hero Banner ── */
.hero-banner {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 40%, #0f172a 100%);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 16px;
    padding: 36px 40px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle at 60% 40%, rgba(99,102,241,0.08) 0%, transparent 60%);
    pointer-events: none;
}
.hero-title {
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #818cf8, #c084fc, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 8px 0;
    line-height: 1.2;
}
.hero-subtitle {
    font-size: 1.05rem;
    color: #94a3b8;
    margin: 0;
    font-weight: 400;
}
.hero-badge {
    display: inline-block;
    background: rgba(16,185,129,0.15);
    border: 1px solid rgba(16,185,129,0.4);
    color: #34d399;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    margin-bottom: 14px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* ── Pipeline Flow Cards ── */
.pipeline-row {
    display: flex;
    gap: 10px;
    margin-bottom: 24px;
    flex-wrap: wrap;
}
.pipeline-step {
    flex: 1;
    min-width: 110px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 14px 12px;
    text-align: center;
    position: relative;
}
.pipeline-step.active {
    border-color: rgba(99,102,241,0.5);
    background: rgba(99,102,241,0.08);
}
.pipeline-step .step-icon { font-size: 1.5rem; display: block; margin-bottom: 5px; }
.pipeline-step .step-label { font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em; }
.pipeline-arrow {
    display: flex;
    align-items: center;
    color: #4f46e5;
    font-size: 1.2rem;
    margin-top: 10px;
}

/* ── Query Box ── */
.query-section {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
}

/* ── Example chip buttons ── */
.example-label {
    font-size: 0.75rem;
    color: #64748b;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 10px;
}

/* ── Result card ── */
.result-card {
    background: linear-gradient(135deg, rgba(15,23,42,0.9), rgba(30,27,75,0.5));
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 14px;
    padding: 28px;
    margin-top: 16px;
    position: relative;
}
.result-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #a855f7, #38bdf8);
    border-radius: 14px 14px 0 0;
}
.result-header {
    font-size: 0.72rem;
    color: #818cf8;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── Metric card ── */
.metric-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 18px 16px;
    margin-bottom: 12px;
}
.metric-label {
    font-size: 0.68rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
    margin-bottom: 6px;
}
.metric-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #f1f5f9;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
}
.metric-value.fast { color: #34d399; }
.metric-value.ok   { color: #fbbf24; }
.metric-value.slow { color: #f87171; }
.metric-sub {
    font-size: 0.7rem;
    color: #475569;
    margin-top: 4px;
}

/* ── Status badge ── */
.status-online {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(16,185,129,0.12);
    border: 1px solid rgba(16,185,129,0.3);
    color: #34d399;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 20px;
}
.dot-pulse {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #34d399;
    animation: pulse 1.5s ease-in-out infinite;
    display: inline-block;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.4; transform: scale(0.8); }
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #080c17;
    border-right: 1px solid rgba(255,255,255,0.06);
}
.sidebar-section {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 14px;
}
.sidebar-title {
    font-size: 0.7rem;
    color: #818cf8;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 12px;
}
.arch-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 12px;
}
.arch-icon {
    font-size: 1.1rem;
    min-width: 24px;
}
.arch-text { font-size: 0.78rem; color: #94a3b8; line-height: 1.5; }
.arch-text strong { color: #e2e8f0; font-weight: 600; }

/* Log line styling */
.log-line {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    padding: 3px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    color: #64748b;
}
.log-line.error { color: #f87171; }
.log-line.warn  { color: #fbbf24; }
.log-line.info  { color: #34d399; }

/* Streamlit element overrides */
div[data-testid="stTextInput"] > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: #f1f5f9 !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
}
div[data-testid="stTextInput"] > div > div > input:focus {
    border-color: rgba(99,102,241,0.5) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
}
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 10px 24px !important;
    transition: opacity 0.2s !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    opacity: 0.85 !important;
}
div[data-testid="stMarkdownContainer"] h3 {
    color: #c084fc !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    margin-top: 20px !important;
    padding-bottom: 6px !important;
    border-bottom: 1px solid rgba(255,255,255,0.06) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:4px 0 20px">
      <div style="font-size:1.1rem;font-weight:800;color:#818cf8;">🛡️ SRE Swarm</div>
      <div style="font-size:0.72rem;color:#475569;margin-top:2px;">AI Ops Platform v2.0</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-section">
      <div class="sidebar-title">⚙️ System Architecture</div>
      <div class="arch-item">
        <span class="arch-icon">📥</span>
        <div class="arch-text"><strong>Data Ingestion</strong><br>Parses server logs & financial PDFs into semantic chunks</div>
      </div>
      <div class="arch-item">
        <span class="arch-icon">🔎</span>
        <div class="arch-text"><strong>Hybrid Retrieval</strong><br>Qdrant dense search + BM25 lexical, re-ranked by Cross-Encoder</div>
      </div>
      <div class="arch-item">
        <span class="arch-icon">🤖</span>
        <div class="arch-text"><strong>Multi-Agent Swarm</strong><br>SRE Agent + FinOps Analyst under a Supervisor node</div>
      </div>
      <div class="arch-item">
        <span class="arch-icon">⚡</span>
        <div class="arch-text"><strong>Groq Cloud LLM</strong><br>Llama 3.1 inference at ~500ms via Groq API</div>
      </div>
      <div class="arch-item">
        <span class="arch-icon">🔒</span>
        <div class="arch-text"><strong>Persistent Memory</strong><br>Qdrant stores long-term context across sessions</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-section">
      <div class="sidebar-title">📡 Backend Status</div>
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
        <span style="font-size:0.78rem;color:#94a3b8;">FastAPI Server</span>
        <span class="status-online"><span class="dot-pulse"></span>Online</span>
      </div>
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
        <span style="font-size:0.78rem;color:#94a3b8;">Groq LLM API</span>
        <span class="status-online"><span class="dot-pulse"></span>Connected</span>
      </div>
      <div style="display:flex;align-items:center;justify-content:space-between;">
        <span style="font-size:0.78rem;color:#94a3b8;">Qdrant Vector DB</span>
        <span class="status-online"><span class="dot-pulse"></span>Loaded</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-section">
      <div class="sidebar-title">🏷️ Data Sources</div>
      <div style="font-size:0.75rem;color:#94a3b8;line-height:1.8;">
        📄 <strong style="color:#e2e8f0;">server_logs.txt</strong><br>
        &nbsp;&nbsp;&nbsp;100 lines · Errors, DB timeouts, 200 OK<br><br>
        📊 <strong style="color:#e2e8f0;">financial_quarterly.pdf</strong><br>
        &nbsp;&nbsp;&nbsp;Cloud billing report · tables & budgets
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Main Content ─────────────────────────────────────────────────────────────

# Hero Banner
st.markdown("""
<div class="hero-banner">
  <div class="hero-badge">● Live · Groq-Powered · Privacy-First</div>
  <div class="hero-title">Enterprise SRE Autonomous<br>Swarm Control Center</div>
  <div class="hero-subtitle">
    Describe any infrastructure incident in plain English. The AI agent will retrieve relevant logs &amp; financial data,
    then deliver an immediate structured root-cause diagnosis — in under 1 second.
  </div>
</div>
""", unsafe_allow_html=True)

# Pipeline Flow Visualization
st.markdown("""
<div class="pipeline-row">
  <div class="pipeline-step">
    <span class="step-icon">📝</span>
    <div class="step-label">Your Query</div>
  </div>
  <div class="pipeline-arrow">→</div>
  <div class="pipeline-step active">
    <span class="step-icon">🔎</span>
    <div class="step-label">Hybrid Retrieval</div>
  </div>
  <div class="pipeline-arrow">→</div>
  <div class="pipeline-step active">
    <span class="step-icon">📚</span>
    <div class="step-label">Context Grounding</div>
  </div>
  <div class="pipeline-arrow">→</div>
  <div class="pipeline-step active">
    <span class="step-icon">🤖</span>
    <div class="step-label">Llama 3.1 (Groq)</div>
  </div>
  <div class="pipeline-arrow">→</div>
  <div class="pipeline-step">
    <span class="step-icon">📋</span>
    <div class="step-label">SRE Report</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Main Columns ─────────────────────────────────────────────────────────────
col_main, col_metrics = st.columns([3, 1], gap="large")

with col_main:
    # Example queries
    st.markdown('<div class="example-label">💡 Try an example query</div>', unsafe_allow_html=True)
    
    example_queries = [
        "What caused the checkout_service OOMKill?",
        "Are there database timeout errors in the logs?",
        "Which services had critical errors?",
        "What is the cloud billing status from the report?",
        "Is the payment service within budget?",
    ]
    
    cols = st.columns(len(example_queries))
    selected_example = None
    for i, (col, q) in enumerate(zip(cols, example_queries)):
        with col:
            if st.button(q[:28] + "…" if len(q) > 28 else q, key=f"ex_{i}", use_container_width=True):
                selected_example = q

    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

    # Query input
    default_val = selected_example if selected_example else ""
    user_query = st.text_input(
        "🔍 Enter your infrastructure incident query:",
        value=default_val,
        placeholder="e.g. What caused the checkout_service to crash? Are DB timeouts related to billing overruns?",
        label_visibility="visible",
    )

    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

    trigger = st.button("⚡  Run Autonomous Triage", type="primary", use_container_width=False)

    # ── Run Triage ──
    if trigger:
        if not user_query.strip():
            st.warning("Please type an incident query above or select an example.")
        else:
            with st.spinner("Agent pipeline executing — retrieving context and running Groq inference…"):
                t0 = time.time()
                try:
                    res = requests.post(
                        "http://localhost:8000/api/triage",
                        json={"query": user_query},
                        timeout=60,
                    )
                    data = res.json()
                    wall_ms = round((time.time() - t0) * 1000, 1)

                    if data.get("status") == "success":
                        # Store for metrics panel
                        st.session_state["last_metrics"] = data["telemetry"]
                        st.session_state["last_answer"] = data["answer"]
                        st.session_state["last_query"] = user_query
                        st.session_state["wall_ms"] = wall_ms
                    else:
                        st.error("Backend returned an error. Check the server logs.")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot reach the FastAPI backend at `localhost:8000`. Make sure it's running.")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")

    # ── Display Result ──
    if "last_answer" in st.session_state:
        st.markdown(f"""
        <div class="result-card">
          <div class="result-header">
            🛡️ AI-Generated Incident Report
            &nbsp;·&nbsp;
            <span style="color:#475569;font-weight:400;text-transform:none;letter-spacing:0;">Query: {st.session_state['last_query']}</span>
          </div>
        """, unsafe_allow_html=True)
        st.markdown(st.session_state["last_answer"])
        st.markdown("</div>", unsafe_allow_html=True)

        # Sample log viewer
        st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
        with st.expander("📄 View Raw Ingested Log Samples (Context Source)"):
            st.markdown("""
            <div class="log-line error">2024-03-15 02:14:32 [ERROR] checkout_service: OOMKilled – container group terminated (pod: checkout-7d9f4b-xk2p)</div>
            <div class="log-line warn"> 2024-03-15 02:13:55 [WARN]  db_pool: connection pool exhausted – 42 timed-out requests queued</div>
            <div class="log-line error">2024-03-15 02:12:01 [ERROR] payment_service: upstream timeout after 30000ms (stripe_api)</div>
            <div class="log-line info"> 2024-03-15 02:10:12 [INFO]  api_gateway: GET /health → 200 OK (latency: 12ms)</div>
            <div class="log-line warn"> 2024-03-15 02:09:48 [WARN]  memory_monitor: checkout_service RSS at 94% of limit (3.76 GB / 4 GB)</div>
            <div class="log-line info"> 2024-03-15 02:08:30 [INFO]  api_gateway: POST /checkout → 200 OK (latency: 234ms)</div>
            <div class="log-line error">2024-03-15 02:07:15 [ERROR] inventory_service: DB query timeout after 5000ms (postgres)</div>
            """, unsafe_allow_html=True)

# ── Metrics Column ────────────────────────────────────────────────────────────
with col_metrics:
    st.markdown("<div style='padding-top:4px'></div>", unsafe_allow_html=True)
    st.markdown("**📊 Pipeline Telemetry**")
    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

    if "last_metrics" in st.session_state:
        m = st.session_state["last_metrics"]
        lat = m["latency_ms"]

        # Latency color coding
        speed_class = "fast" if lat < 1000 else "ok" if lat < 5000 else "slow"
        speed_label = "🟢 Fast" if lat < 1000 else "🟡 Normal" if lat < 5000 else "🔴 Slow"

        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">⏱ Inference Latency</div>
          <div class="metric-value {speed_class}">{lat:,.0f} ms</div>
          <div class="metric-sub">{speed_label} · Groq Cloud</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">📥 Prompt Tokens</div>
          <div class="metric-value">{m['prompt_tokens']}</div>
          <div class="metric-sub">Context + System Prompt</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">📤 Completion Tokens</div>
          <div class="metric-value">{m['completion_tokens']}</div>
          <div class="metric-sub">Generated SRE Report</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">💰 Est. API Cost</div>
          <div class="metric-value fast">$0.00</div>
          <div class="metric-sub">Groq Free Tier</div>
        </div>
        """, unsafe_allow_html=True)

        # Token efficiency bar
        total = m["prompt_tokens"] + m["completion_tokens"]
        pct = int((m["completion_tokens"] / total) * 100) if total > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">⚖️ Token Efficiency</div>
          <div style="background:rgba(255,255,255,0.06);border-radius:6px;height:8px;margin:10px 0 6px;">
            <div style="background:linear-gradient(90deg,#6366f1,#a855f7);width:{pct}%;height:100%;border-radius:6px;"></div>
          </div>
          <div class="metric-sub">{pct}% of tokens = output signal</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="metric-card" style="text-align:center;padding:30px 16px;">
          <div style="font-size:2rem;margin-bottom:10px;">⏳</div>
          <div style="font-size:0.8rem;color:#475569;line-height:1.6;">
            Telemetry will appear here<br>after your first query.
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-label">🎯 Target Latency</div>
          <div class="metric-value fast">&lt; 1s</div>
          <div class="metric-sub">Groq Cloud endpoint</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">🏗️ LLM Model</div>
          <div style="font-size:0.82rem;color:#818cf8;font-family:'JetBrains Mono',monospace;margin-top:4px;">llama-3.1-8b-instant</div>
          <div class="metric-sub">via Groq API</div>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<div style='margin-top:48px'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="border-top:1px solid rgba(255,255,255,0.06);padding-top:16px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
  <div style="font-size:0.72rem;color:#334155;">
    🛡️ <strong style="color:#818cf8;">SRE Autonomous Swarm</strong> · Built with FastAPI + Streamlit + Groq + Qdrant
  </div>
  <div style="font-size:0.72rem;color:#334155;">
    Days 1–10 · RAG · Hybrid Search · Multi-Agent · LLMOps · Full-Stack UI
  </div>
</div>
""", unsafe_allow_html=True)
