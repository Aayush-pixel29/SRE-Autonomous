from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
import numpy as np

# 1. Initialize DB and Models
client = QdrantClient(path="./local_qdrant_db")
COLLECTION_NAME = "enterprise_ops_data"
encoder = SentenceTransformer('all-MiniLM-L6-v2')

# High-accuracy cross-encoder for re-ranking
re_ranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# 2. Fetch all payload data from Qdrant to build a local BM25 index for keyword search
print("Building lexical index from existing collection...")
all_points = client.scroll(collection_name=COLLECTION_NAME, limit=100)[0]
corpus = [p.payload["page_content"] for p in all_points]
tokenized_corpus = [doc.lower().split(" ") for doc in corpus]
bm25 = BM25Okapi(tokenized_corpus)

def hybrid_search(query, top_k=5):
    # --- Part A: Dense Semantic Search ---
    query_vector = encoder.encode(query).tolist()
    # Using query_points as client.search is deprecated/unavailable on this local Qdrant Client version
    dense_results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    )
    
    # --- Part B: Lexical Keyword Search (BM25) ---
    tokenized_query = query.lower().split(" ")
    bm25_scores = bm25.get_scores(tokenized_query)
    top_bm25_indices = np.argsort(bm25_scores)[::-1][:top_k]
    
    # --- Part C: Combine Candidates (De-duplicate) ---
    candidate_chunks = set()
    for hit in dense_results.points:
        candidate_chunks.add(hit.payload["page_content"])
    for idx in top_bm25_indices:
        if bm25_scores[idx] > 0: # Only keep meaningful keyword hits
            candidate_chunks.add(corpus[idx])
            
    candidate_list = list(candidate_chunks)
    
    # --- Part D: Cross-Encoder Re-ranking ---
    print(f"Evaluating {len(candidate_list)} unified candidates via Cross-Encoder...")
    pairs = [[query, doc] for doc in candidate_list]
    scores = re_ranker.predict(pairs)
    
    # Sort by re-ranker confidence score
    ranked_results = sorted(zip(scores, candidate_list), key=lambda x: x[0], reverse=True)
    
    return ranked_results[:3]

# 3. Test Drive the Search System
if __name__ == "__main__":
    test_query = "Find connection timeout errors or financial overspending records"
    print(f"\n--- Running Hybrid Query: '{test_query}' ---")
    results = hybrid_search(test_query)
    
    for i, (score, content) in enumerate(results):
        print(f"\n[Rank {i+1}] Re-rank Score: {score:.4f}")
        print(f"Content Summary: {content[:150]}...")
