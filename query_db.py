from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Initialize Local Components
print("Initializing embedding model and local Qdrant DB...")
encoder = SentenceTransformer('all-MiniLM-L6-v2')
client = QdrantClient(path="./local_qdrant_db")

COLLECTION_NAME = "enterprise_ops_data"

# Define a query
query_text = "database connection timeout or pool exhaustion"
print(f"\nSearching for: '{query_text}'...")

# Generate query vector
query_vector = encoder.encode(query_text).tolist()

# Search in Qdrant
results = client.query_points(
    collection_name=COLLECTION_NAME,
    query=query_vector,
    limit=3
)

# Print results
print("\n--- Search Results ---")
for idx, hit in enumerate(results.points):
    print(f"\nResult #{idx + 1} (Score: {hit.score:.4f})")
    print(f"Source: {hit.payload.get('source')} ({hit.payload.get('data_type')})")
    print(f"Content:\n{hit.payload.get('page_content')}")
