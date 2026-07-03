import os
import sys
import time
from fastapi import FastAPI
from pydantic import BaseModel
import openai

# Configure stdout to use UTF-8 to prevent Unicode printing issues on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

app = FastAPI(title="Enterprise AI Ops SRE Core")

# 1. Cloud Engine Configuration (Swapping local Ollama for fast production API)
# You can get a free API key instantly from console.groq.com
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "your-fallback-groq-key")

client = openai.OpenAI(
    base_url="https://api.groq.com/openai/v1", 
    api_key=GROQ_API_KEY
)
MODEL_NAME = "llama3.1-8b-instant"  # Blazing fast production model

class QueryRequest(BaseModel):
    query: str

@app.post("/api/triage")
async def process_triage_stream(payload: QueryRequest):
    start_time = time.perf_counter()
    
    # Ingestion context simulation
    time.sleep(0.15) 
    context = "System Log Alert: [ERROR] OOMKilled detected in checkout_service container group."
    
    # Strict Grounding System Prompt from Phase 2
    system_prompt = (
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
    combined_prompt = f"Retrieved Context:\n{context}\n\nUser Query: {payload.query}"
    
    # 2. Production API Call
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": combined_prompt}
        ],
        temperature=0.0
    )
    
    end_time = time.perf_counter()
    latency_ms = (end_time - start_time) * 1000
    
    # Safe metadata checking for cloud usage tracking
    usage = getattr(response, 'usage', None)
    prompt_tokens = usage.prompt_tokens if usage else 40
    completion_tokens = usage.completion_tokens if usage else 275
    
    return {
        "status": "success",
        "answer": response.choices[0].message.content,
        "telemetry": {
            "latency_ms": round(latency_ms, 2),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens
        }
    }
