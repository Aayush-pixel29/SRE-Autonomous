import sys
import time
import functools
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

# Configure stdout to use UTF-8 to prevent Unicode printing issues on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Initialize our local engine
llm = ChatOllama(model="llama3.1", temperature=0.0)

# --- 1. LLMOps Telemetry Decorator ---
def trace_execution(step_name: str):
    """A production-grade decorator to track latency and log metrics for agent operations."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(f"\n⏱️  [TRACE START] Entering Step: {step_name}")
            start_time = time.perf_counter()
            
            try:
                result = func(*args, **kwargs)
                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000
                print(f"✅ [TRACE END] Completed: {step_name} | Latency: {latency_ms:.2f}ms")
                return result
            except Exception as e:
                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000
                print(f"❌ [TRACE ERROR] Failed: {step_name} | Latency: {latency_ms:.2f}ms | Error: {str(e)}")
                raise e
        return wrapper
    return decorator

# --- 2. Mock Traced Components ---
@trace_execution("Vector DB Context Ingestion")
def mock_vector_db_lookup(query: str):
    # Simulating a local vector storage look up delay
    time.sleep(0.25) 
    return "Sample contextual log match from database store."

@trace_execution("Local LLM Inference Engine Turn")
def call_local_llm(prompt_payload: str):
    messages = [HumanMessage(content=prompt_payload)]
    response = llm.invoke(messages)
    
    # Extract native metadata token counts if supported by the provider response
    meta = response.response_metadata.get("token_usage", {})
    usage = getattr(response, "usage_metadata", None)
    if usage:
        prompt_tokens = usage.get("input_tokens", "N/A")
        completion_tokens = usage.get("output_tokens", "N/A")
    else:
        prompt_tokens = meta.get("prompt_tokens", "N/A")
        completion_tokens = meta.get("completion_tokens", "N/A")
    
    print(f"📊 [Metrics Evaluator] Prompt Tokens: {prompt_tokens} | Completion Tokens: {completion_tokens}")
    return response.content

# --- 3. Orchestrated Execution Wrapper ---
@trace_execution("End-to-End Managed Agent Pipeline")
def run_monitored_pipeline(user_query: str):
    context = mock_vector_db_lookup(user_query)
    combined_input = f"Context: {context}\n\nQuery: {user_query}"
    final_output = call_local_llm(combined_input)
    return final_output

if __name__ == "__main__":
    print("=== Launching Monitored SRE Pipeline Run ===")
    test_query = "Summarize the active infrastructure problems on checkout_service."
    
    pipeline_result = run_monitored_pipeline(test_query)
    print("\n[Pipeline Result Output]:")
    print(pipeline_result)
