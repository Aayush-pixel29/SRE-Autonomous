import sys
import openai
from retrieve import hybrid_search

# Configure stdout to use UTF-8 to prevent Unicode printing issues on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# 1. Directing the client to your local Docker-hosted Ollama container
client = openai.OpenAI(
    base_url="http://localhost:11434/v1", 
    api_key="ollama"  # Ollama doesn't require a real API key, but the client wrapper needs a non-empty string
)
MODEL_NAME = "llama3"

def generate_grounded_analysis(query: str) -> str:
    print(f"\n[RAG] Retrieving context for query: '{query}'...")
    retrieved_hits = hybrid_search(query, top_k=5)
    
    # Construct context block from payloads
    context_str = ""
    for idx, (score, content) in enumerate(retrieved_hits):
        context_str += f"--- Document Source Snapshot #{idx+1} ---\n{content}\n\n"
        
    # Strict Grounding System Prompt
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
    
    user_prompt = f"Retrieved Context:\n{context_str}\n\nUser Query: {query}"
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0  # Zero out creativity for deterministic structural evaluation
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Execution Error: {str(e)}"

if __name__ == "__main__":
    # Test 1: Evaluating overlapping records across logs and PDFs
    valid_query = "What caused the checkout service to fail, and how does it relate to our June latency targets?"
    print("\n--- Running Test 1 (Valid Context Data) ---")
    print(generate_grounded_analysis(valid_query))
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Testing out-of-bounds guardrails
    invalid_query = "What was our marketing budget spend for Q3 on Google Ads?"
    print("--- Running Test 2 (Out-of-Bounds Context Data) ---")
    print(generate_grounded_analysis(invalid_query))
