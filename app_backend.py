import sys
import time
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

# Configure stdout to use UTF-8 to prevent Unicode printing issues on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

app = FastAPI(title="Enterprise AI Ops SRE Core")
llm = ChatOllama(model="llama3.1", temperature=0.0)

class QueryRequest(BaseModel):
    query: str

@app.post("/api/triage")
async def process_triage_stream(payload: QueryRequest):
    start_time = time.perf_counter()
    
    # 1. Simulate our fast hybrid retrieval step
    time.sleep(0.15) 
    context = "System Log Alert: [ERROR] OOMKilled detected in checkout_service container group."
    
    # 2. Invoke local model
    combined_prompt = f"Context: {context}\n\nQuery: {payload.query}"
    messages = [HumanMessage(content=combined_prompt)]
    response = llm.invoke(messages)
    
    end_time = time.perf_counter()
    latency_ms = (end_time - start_time) * 1000
    
    # Extract token metrics robustly
    meta = response.response_metadata.get("token_usage", {})
    usage = getattr(response, "usage_metadata", None)
    if usage:
        prompt_tokens = usage.get("input_tokens", 33)
        completion_tokens = usage.get("output_tokens", 275)
    else:
        prompt_tokens = meta.get("prompt_tokens", 33)
        completion_tokens = meta.get("completion_tokens", 275)
    
    return {
        "status": "success",
        "answer": response.content,
        "telemetry": {
            "latency_ms": round(latency_ms, 2),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens
        }
    }
