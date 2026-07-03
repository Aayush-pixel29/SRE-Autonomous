# Enterprise AI Ops: Autonomous SecOps & SRE Swarm Agent

A privacy-first, fully local multi-agent system designed to automate root-cause analysis (RAG) and infrastructure incident mitigation while enforcing strict cloud fiscal (FinOps) guardrails.

## 🏗️ Architectural Overview
- **Data Ingestion Layer**: Automatic parsing of unstructured application text logs and structured financial/billing PDFs using a local vector pipeline.
- **Hybrid Retrieval System**: Combined Dense Semantic Search (Qdrant DB) + Lexical Keyword Search (BM25) re-ranked via a Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) to eliminate log keywords noise.
- **Orchestration & State Machine**: Built stateful routing and parallel tool calling via a local `llama3.1` model.
- **Multi-Agent Swarm**: Specialized task delegation using an Infrastructure SRE Agent (hardware mitigation) and a FinOps Analyst Agent (budget compliance verification) acting under a Supervisor node.
- **Full-Stack Interface**: Decoupled asynchronous backend (FastAPI) paired with a reactive analytics panel (Streamlit).

## 📊 Performance & Telemetry Profile (Local Execution)
- **Vector DB Extraction Latency**: ~250ms (Deterministic cosine distance matching)
- **Average Token Footprint**: 40 Prompt Tokens | ~275 Completion Tokens
- **Data Residency**: 100% Offline / Local Docker Infrastructure

## 🚀 Local Deployment Step-by-Step
```bash
# Spin up local LLM weights
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
docker exec -it ollama ollama run llama3.1

# Initialize full-stack endpoints
uvicorn app_backend:app --host 0.0.0.0 --port 8000
streamlit run app_frontend.py
```
