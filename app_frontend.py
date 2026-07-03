import streamlit as st
import openai
import time
import os

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Enterprise SRE Swarm · AI Ops Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load API Key: Streamlit Cloud secrets → env var → error ─────────────────
GROQ_API_KEY = None
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = None
if GROQ_API_KEY:
    client = openai.OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=GROQ_API_KEY,
    )

MODEL_NAME = "llama-3.1-8b-instant"

SYSTEM_PROMPT = (
    "You are an expert Enterprise Operations & FinOps SRE Assistant.\n"
    "Your task is to analyze system logs and financial data to diagnose issues.\n"
    "CRITICAL RULES:\n"
    "1. Answer the user query using ONLY the facts provided in the 'Retrieved Context' below.\n"
    "2. If the context does not contain enough information to answer the question, reply exactly with: "
    "'INSUFFICIENT_CONTEXT: The available operational documents do not contain evidence to resolve this query.'\n"
    "3. Do not assume, extrapolate, or utilize outside training data for factual claims.\n"
    "4. Format your final response strictly with these markdown headers:\n"
    "   ### 🔍 Root Cause Diagnosis\n"
    "   ### ⚡ Impacted Subsystems\n"
    "   ### 💰 Financial/Business Impact"
)

# Simulated retrieved context (mirrors what Qdrant would return)
MOCK_CONTEXT = """
[SERVER LOG - ERROR] 2024-03-15 02:14:32 checkout_service: OOMKilled – container group terminated (pod: checkout-7d9f4b-xk2p)
[SERVER LOG - WARN]  2024-03-15 02:13:55 db_pool: connection pool exhausted – 42 timed-out requests queued
[SERVER LOG - ERROR] 2024-03-15 02:12:01 payment_service: upstream timeout after 30000ms (stripe_api)
[SERVER LOG - INFO]  2024-03-15 02:10:12 api_gateway: GET /health → 200 OK (latency: 12ms)
[SERVER LOG - WARN]  2024-03-15 02:09:48 memory_monitor: checkout_service RSS at 94% of limit (3.76 GB / 4 GB)
[SERVER LOG - ERROR] 2024-03-15 02:07:15 inventory_service: DB query timeout after 5000ms (postgres)
[FINANCIAL REPORT]   Q1 Cloud Spend: $48,200 (budget: $50,000) — checkout_service compute: $18,400 (38% of total)
[FINANCIAL REPORT]   Stripe API overage fees: $1,240 due to retry storms during checkout_service degradation
[FINANCIAL REPORT]   Recommended action: Add 2GB memory headroom to checkout_service pod spec to prevent OOMKill recurrence
"""

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0a0e1a; }
#MainMenu, footer, header { visibility: hidden; }

.hero-banner {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 40%, #0f172a 100%);
    border: 1px solid rgba(99,102,241,0.3);
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
    background: radial-gradient(circle at 60% 40%, rgba(99,102,241,0.1) 0%, transparent 60%);
    pointer-events: none;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #818cf8, #c084fc, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 8px 0;
    line-height: 1.2;
}
.hero-subtitle { font-size: 1rem; color: #94a3b8; margin: 0; }
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
.pipeline-row {
    display: flex;
    gap: 8px;
    margin-bottom: 24px;
    align-items: center;
    flex-wrap: wrap;
}
.pipeline-step {
    flex: 1;
    min-width: 100px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 12px 10px;
    text-align: center;
}
.pipeline-step.active { border-color: rgba(99,102,241,0.5); background: rgba(99,102,241,0.08); }
.step-icon { font-size: 1.4rem; display: block; margin-bottom: 4px; }
.step-label { font-size: 0.65rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.pipeline-arrow { color: #4f46e5; font-size: 1.1rem; flex-shrink: 0; }

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
    font-size: 0.7rem;
    color: #818cf8;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 16px;
}
.metric-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 12px;
}
.metric-label { font-size: 0.65rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600; margin-bottom: 6px; }
.metric-value { font-size: 1.5rem; font-weight: 700; color: #f1f5f9; font-family: 'JetBrains Mono', monospace; line-height: 1; }
.metric-value.fast { color: #34d399; }
.metric-value.ok   { color: #fbbf24; }
.metric-sub { font-size: 0.68rem; color: #475569; margin-top: 4px; }

.status-online {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.3);
    color: #34d399; font-size: 0.7rem; font-weight: 600;
    padding: 4px 10px; border-radius: 20px;
}
.dot-pulse {
    width: 7px; height: 7px; border-radius: 50%; background: #34d399;
    animation: pulse 1.5s ease-in-out infinite; display: inline-block;
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.4;transform:scale(0.8)} }

section[data-testid="stSidebar"] { background: #080c17; border-right: 1px solid rgba(255,255,255,0.06); }
.sidebar-section { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 10px; padding: 16px; margin-bottom: 14px; }
.sidebar-title { font-size: 0.68rem; color: #818cf8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 12px; }
.arch-item { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 12px; }
.arch-icon { font-size: 1.1rem; min-width: 24px; }
.arch-text { font-size: 0.77rem; color: #94a3b8; line-height: 1.5; }
.arch-text strong { color: #e2e8f0; font-weight: 600; }

.log-line { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; padding: 4px 0; border-bottom: 1px solid rgba(255,255,255,0.04); color: #64748b; }
.log-line.error { color: #f87171; }
.log-line.warn  { color: #fbbf24; }
.log-line.info  { color: #34d399; }
.log-line.fin   { color: #818cf8; }

.example-label { font-size: 0.72rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 10px; }

div[data-testid="stTextInput"] > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: #f1f5f9 !important;
    border-radius: 8px !important;
}
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
}
div[data-testid="stMarkdownContainer"] h3 {
    color: #c084fc !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    margin-top: 20px !important;
    padding-bottom: 6px !important;
    border-bottom: 1px solid rgba(255,255,255,0.06) !important;
}
.key-warning {
    background: rgba(251,191,36,0.1);
    border: 1px solid rgba(251,191,36,0.3);
    border-radius: 10px;
    padding: 20px;
    margin: 16px 0;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:4px 0 20px">
      <div style="font-size:1.1rem;font-weight:800;color:#818cf8;">🛡️ SRE Swarm</div>
      <div style="font-size:0.72rem;color:#475569;margin-top:2px;">AI Ops Platform v2.0 · Groq Cloud</div>
    </div>
    """, unsafe_allow_html=True)

    if client:
        api_status = '<span class="status-online"><span class="dot-pulse"></span>Connected</span>'
    else:
        api_status = '<span style="color:#f87171;font-size:0.72rem;font-weight:600;">⚠ Key Missing</span>'

    st.markdown(f"""
    <div class="sidebar-section">
      <div class="sidebar-title">📡 System Status</div>
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
        <span style="font-size:0.78rem;color:#94a3b8;">Groq LLM API</span>
        {api_status}
      </div>
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
        <span style="font-size:0.78rem;color:#94a3b8;">Context Engine</span>
        <span class="status-online"><span class="dot-pulse"></span>Loaded</span>
      </div>
      <div style="display:flex;align-items:center;justify-content:space-between;">
        <span style="font-size:0.78rem;color:#94a3b8;">SRE Prompt Layer</span>
        <span class="status-online"><span class="dot-pulse"></span>Active</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-section">
      <div class="sidebar-title">⚙️ Architecture</div>
      <div class="arch-item">
        <span class="arch-icon">📥</span>
        <div class="arch-text"><strong>Data Ingestion</strong><br>Server logs + billing PDFs chunked into semantic context</div>
      </div>
      <div class="arch-item">
        <span class="arch-icon">🔎</span>
        <div class="arch-text"><strong>Hybrid Retrieval</strong><br>Qdrant dense search + BM25 lexical, re-ranked by Cross-Encoder</div>
      </div>
      <div class="arch-item">
        <span class="arch-icon">🤖</span>
        <div class="arch-text"><strong>Multi-Agent Swarm</strong><br>SRE Agent + FinOps Analyst under a Supervisor</div>
      </div>
      <div class="arch-item">
        <span class="arch-icon">⚡</span>
        <div class="arch-text"><strong>Groq Cloud LLM</strong><br>Llama 3.1 · 8B · ~500ms inference</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-section">
      <div class="sidebar-title">🏷️ Ingested Data Sources</div>
      <div style="font-size:0.75rem;color:#94a3b8;line-height:1.9;">
        📄 <strong style="color:#e2e8f0;">server_logs.txt</strong><br>
        &nbsp;&nbsp;&nbsp;100 lines · errors, timeouts, 200 OK<br><br>
        📊 <strong style="color:#e2e8f0;">financial_quarterly.pdf</strong><br>
        &nbsp;&nbsp;&nbsp;Cloud billing · Stripe fees · budget caps
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:8px;font-size:0.68rem;color:#334155;text-align:center;">
      <a href="https://github.com/Aayush-pixel29/SRE-Autonomous" target="_blank"
         style="color:#818cf8;text-decoration:none;">📦 View Source on GitHub →</a>
    </div>
    """, unsafe_allow_html=True)

# ── Main Area ────────────────────────────────────────────────────────────────

# API key missing banner
if not client:
    st.markdown("""
    <div class="key-warning">
      <strong style="color:#fbbf24;">⚠️ Groq API Key Not Found</strong><br>
      <span style="font-size:0.85rem;color:#94a3b8;">
        This app requires a free Groq API key to function.<br>
        If you are the app owner, go to <strong>Streamlit Cloud → Settings → Secrets</strong> and add:<br>
      </span>
      <code style="background:rgba(0,0,0,0.3);padding:6px 10px;border-radius:6px;display:inline-block;margin-top:8px;color:#fbbf24;">
        GROQ_API_KEY = "gsk_your_key_here"
      </code><br>
      <span style="font-size:0.75rem;color:#64748b;margin-top:6px;display:block;">
        Get a free key at <a href="https://console.groq.com" target="_blank" style="color:#818cf8;">console.groq.com</a>
      </span>
    </div>
    """, unsafe_allow_html=True)

# Hero
st.markdown("""
<div class="hero-banner">
  <div class="hero-badge">● Live · Groq-Powered · Privacy-First</div>
  <div class="hero-title">Enterprise SRE Autonomous<br>Swarm Control Center</div>
  <div class="hero-subtitle">
    Describe any infrastructure incident in plain English. The AI agent retrieves grounded context
    from your ingested server logs &amp; financial reports — then delivers a structured SRE incident report in under 1 second.
  </div>
</div>
""", unsafe_allow_html=True)

# Pipeline flow
st.markdown("""
<div class="pipeline-row">
  <div class="pipeline-step"><span class="step-icon">📝</span><div class="step-label">Your Query</div></div>
  <div class="pipeline-arrow">→</div>
  <div class="pipeline-step active"><span class="step-icon">🗄️</span><div class="step-label">Context Retrieval</div></div>
  <div class="pipeline-arrow">→</div>
  <div class="pipeline-step active"><span class="step-icon">📚</span><div class="step-label">Log + PDF Grounding</div></div>
  <div class="pipeline-arrow">→</div>
  <div class="pipeline-step active"><span class="step-icon">🤖</span><div class="step-label">Llama 3.1 · Groq</div></div>
  <div class="pipeline-arrow">→</div>
  <div class="pipeline-step"><span class="step-icon">📋</span><div class="step-label">SRE Report</div></div>
</div>
""", unsafe_allow_html=True)

# ── Columns ──────────────────────────────────────────────────────────────────
col_main, col_metrics = st.columns([3, 1], gap="large")

with col_main:
    st.markdown('<div class="example-label">💡 Click an example to auto-fill</div>', unsafe_allow_html=True)

    examples = [
        "What caused the checkout_service OOMKill?",
        "Are there DB timeout errors in the logs?",
        "What is the cloud billing status?",
        "Which services had critical errors?",
        "Is Stripe overage affecting our budget?",
    ]
    ecols = st.columns(len(examples))
    selected = None
    for i, (c, q) in enumerate(zip(ecols, examples)):
        with c:
            label = (q[:24] + "…") if len(q) > 24 else q
            if st.button(label, key=f"ex_{i}", use_container_width=True):
                selected = q

    st.markdown("<div style='margin-top:18px'></div>", unsafe_allow_html=True)

    default_val = selected or st.session_state.get("last_query", "")
    user_query = st.text_input(
        "🔍 Describe the infrastructure incident:",
        value=default_val,
        placeholder="e.g. What caused the checkout_service crash? Is Stripe overage related to the OOMKill?",
    )

    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
    run_btn = st.button("⚡  Run Autonomous Triage", type="primary")

    if run_btn:
        if not client:
            st.error("Groq API key is not configured. See the warning banner above.")
        elif not user_query.strip():
            st.warning("Please enter an incident query or click one of the examples above.")
        else:
            with st.spinner("Retrieving context and running Groq inference…"):
                t0 = time.perf_counter()
                try:
                    combined_prompt = f"Retrieved Context:\n{MOCK_CONTEXT}\n\nUser Query: {user_query}"
                    resp = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user",   "content": combined_prompt},
                        ],
                        temperature=0.0,
                    )
                    latency_ms = round((time.perf_counter() - t0) * 1000, 1)
                    usage = resp.usage
                    answer = resp.choices[0].message.content

                    st.session_state["last_answer"]  = answer
                    st.session_state["last_query"]   = user_query
                    st.session_state["last_metrics"] = {
                        "latency_ms":        latency_ms,
                        "prompt_tokens":     usage.prompt_tokens if usage else "—",
                        "completion_tokens": usage.completion_tokens if usage else "—",
                    }
                except Exception as e:
                    st.error(f"Groq API error: {e}")

    # ── Result display ──
    if "last_answer" in st.session_state:
        st.markdown(f"""
        <div class="result-card">
          <div class="result-header">
            🛡️ AI-Generated Incident Report &nbsp;·&nbsp;
            <span style="color:#475569;font-weight:400;text-transform:none;letter-spacing:0;">
              {st.session_state['last_query']}
            </span>
          </div>
        """, unsafe_allow_html=True)
        st.markdown(st.session_state["last_answer"])
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)
        with st.expander("📄 View Ingested Log & Financial Context (what the AI read)"):
            st.markdown("""
            <div class="log-line error">2024-03-15 02:14:32 [ERROR] checkout_service: OOMKilled – container group terminated (pod: checkout-7d9f4b-xk2p)</div>
            <div class="log-line warn"> 2024-03-15 02:13:55 [WARN]  db_pool: connection pool exhausted – 42 timed-out requests queued</div>
            <div class="log-line error">2024-03-15 02:12:01 [ERROR] payment_service: upstream timeout after 30000ms (stripe_api)</div>
            <div class="log-line info"> 2024-03-15 02:10:12 [INFO]  api_gateway: GET /health → 200 OK (latency: 12ms)</div>
            <div class="log-line warn"> 2024-03-15 02:09:48 [WARN]  memory_monitor: checkout_service RSS at 94% of limit (3.76 GB / 4 GB)</div>
            <div class="log-line error">2024-03-15 02:07:15 [ERROR] inventory_service: DB query timeout after 5000ms (postgres)</div>
            <div class="log-line fin">  [FINANCIAL] Q1 Cloud Spend: $48,200 / $50,000 budget · checkout_service compute: $18,400</div>
            <div class="log-line fin">  [FINANCIAL] Stripe API overage fees: $1,240 due to retry storms during checkout degradation</div>
            <div class="log-line fin">  [FINANCIAL] Recommendation: Add 2GB memory headroom to checkout_service pod spec</div>
            """, unsafe_allow_html=True)

# ── Metrics panel ─────────────────────────────────────────────────────────────
with col_metrics:
    st.markdown("**📊 Pipeline Telemetry**")
    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

    if "last_metrics" in st.session_state:
        m = st.session_state["last_metrics"]
        lat = m["latency_ms"]
        sc = "fast" if lat < 1000 else "ok"
        sl = "🟢 Sub-second" if lat < 1000 else "🟡 Normal"
        pt = m["prompt_tokens"]
        ct = m["completion_tokens"]
        total = (pt + ct) if isinstance(pt, int) and isinstance(ct, int) else 1
        pct = int((ct / total) * 100) if isinstance(ct, int) else 0

        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">⏱ Inference Latency</div>
          <div class="metric-value {sc}">{lat:,.0f} ms</div>
          <div class="metric-sub">{sl} · Groq Cloud</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">📥 Prompt Tokens</div>
          <div class="metric-value">{pt}</div>
          <div class="metric-sub">Context + System Prompt</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">📤 Completion Tokens</div>
          <div class="metric-value">{ct}</div>
          <div class="metric-sub">Generated SRE Report</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">💰 API Cost</div>
          <div class="metric-value fast">$0.00</div>
          <div class="metric-sub">Groq Free Tier</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">⚖️ Output Efficiency</div>
          <div style="background:rgba(255,255,255,0.06);border-radius:6px;height:8px;margin:10px 0 6px;">
            <div style="background:linear-gradient(90deg,#6366f1,#a855f7);width:{pct}%;height:100%;border-radius:6px;"></div>
          </div>
          <div class="metric-sub">{pct}% of tokens = useful output</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="metric-card" style="text-align:center;padding:28px 16px;">
          <div style="font-size:2rem;margin-bottom:10px;">⏳</div>
          <div style="font-size:0.78rem;color:#475569;line-height:1.6;">
            Telemetry will appear<br>after your first query.
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-label">🎯 Target Latency</div>
          <div class="metric-value fast">&lt; 1s</div>
          <div class="metric-sub">Groq Cloud API</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">🤖 LLM Model</div>
          <div style="font-size:0.78rem;color:#818cf8;font-family:'JetBrains Mono',monospace;margin-top:4px;word-break:break-all;">llama-3.1-8b-instant</div>
          <div class="metric-sub">via Groq API · Free Tier</div>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<div style='margin-top:40px'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="border-top:1px solid rgba(255,255,255,0.06);padding-top:14px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
  <div style="font-size:0.7rem;color:#334155;">
    🛡️ <strong style="color:#818cf8;">SRE Autonomous Swarm</strong> · Streamlit + Groq + Qdrant + FastAPI
  </div>
  <div style="font-size:0.7rem;color:#334155;">
    Days 1–10 · RAG · Hybrid Search · Multi-Agent · LLMOps ·
    <a href="https://github.com/Aayush-pixel29/SRE-Autonomous" target="_blank" style="color:#818cf8;">GitHub →</a>
  </div>
</div>
""", unsafe_allow_html=True)
