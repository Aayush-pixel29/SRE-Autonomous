import sys
import uuid
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# Configure stdout to use UTF-8 to prevent Unicode printing issues on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# 1. Initialize DB and Models
client = QdrantClient(path="./local_qdrant_db")
MEMORY_COLLECTION = "agent_long_term_memory"
encoder = SentenceTransformer('all-MiniLM-L6-v2')
llm = ChatOllama(model="llama3.1", temperature=0.0)

# Ensure our permanent memory collection is initialized
if not client.collection_exists(collection_name=MEMORY_COLLECTION):
    client.create_collection(
        collection_name=MEMORY_COLLECTION,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

# 2. Long-Term Memory Utilities
def recall_relevant_memories(user_query: str, limit=2) -> str:
    """Queries the long-term memory vector collection for past context."""
    query_vector = encoder.encode(user_query).tolist()
    # Using query_points as client.search is deprecated/unavailable on this local Qdrant Client version
    hits_response = client.query_points(
        collection_name=MEMORY_COLLECTION,
        query=query_vector,
        limit=limit
    )
    hits = hits_response.points
    if not hits:
        return "No relevant historical long-term memories found."
    
    memory_context = "\n".join([f"• Past Event ({hit.payload['date']}): {hit.payload['fact']}" for hit in hits])
    return memory_context

def commit_to_long_term_memory(fact_text: str):
    """Encodes and commits a vital operational fact permanently to Qdrant."""
    print(f"💾 [Memory System] Archiving permanent fact to Qdrant: '{fact_text}'")
    vector = encoder.encode(fact_text).tolist()
    client.upsert(
        collection_name=MEMORY_COLLECTION,
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={"fact": fact_text, "date": "2026-07-03"}
            )
        ]
    )

# 3. Main Memory-Enhanced Conversation Cycle
def run_memory_chat_turn(user_input: str, short_term_history: list) -> str:
    print(f"\n💬 [User]: {user_input}")
    
    # Step A: Extract long-term background facts via vector similarity matching
    historical_background = recall_relevant_memories(user_input)
    print(f"🧠 [Long-Term Memory Retrieved]:\n{historical_background}")
    
    # Step B: Construct full state context (System Instructions + Long-term + Short-term conversation buffer)
    system_prompt = (
        "You are an SRE Assistant equipped with persistent episodic memory layers.\n"
        "Incorporate relevant historical facts and short-term dialogue details naturally into your responses.\n"
        f"Historical Context:\n{historical_background}"
    )
    
    messages = [SystemMessage(content=system_prompt)] + short_term_history + [HumanMessage(content=user_input)]
    
    # Step C: Infer
    response = llm.invoke(messages)
    return response.content

if __name__ == "__main__":
    # Initialize an empty list acting as our ephemeral short-term session window
    session_chat_buffer = []
    
    # --- PHASE A: Seed the Long-Term Memory ---
    # Imagine we ran a triage session yesterday and discovered something critical. Let's save it.
    commit_to_long_term_memory(
        "The checkout_service requires a minimum JVM memory headroom buffer of 4GB due to unoptimized third-party stripe dependencies."
    )
    print("\n" + "="*60 + "\n")
    
    # --- PHASE B: Start New Session & Trigger Memory Retrieval ---
    # We ask a general query in a brand-new session. Let's see if the agent recalls yesterday's structural fact.
    turn_1_query = "We are modifying the infrastructure constraints for checkout_service. Any past settings I should remember?"
    
    reply_1 = run_memory_chat_turn(turn_1_query, session_chat_buffer)
    print(f"\n🤖 [Agent]:\n{reply_1}")
    
    # Update our short-term session window
    session_chat_buffer.append(HumanMessage(content=turn_1_query))
    session_chat_buffer.append(AIMessage(content=reply_1))
    
    print("\n" + "="*60 + "\n")
    
    # --- PHASE C: Multi-Turn Conversation Check (Short-Term Reference) ---
    # We ask a question that requires short-term dialogue memory without restating context.
    turn_2_query = "Understood. How much minimum memory headroom did you say it needed again?"
    
    reply_2 = run_memory_chat_turn(turn_2_query, session_chat_buffer)
    print(f"\n🤖 [Agent]:\n{reply_2}")
