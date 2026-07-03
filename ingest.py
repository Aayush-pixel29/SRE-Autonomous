import os
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# 1. Initialize Local Components
print("Initializing embedding model and local Qdrant DB...")
# Lightweight, high-performance local text embedder (384 dimensions)
encoder = SentenceTransformer('all-MiniLM-L6-v2')
# Initialize Qdrant as a local persistent storage folder
client = QdrantClient(path="./local_qdrant_db")

COLLECTION_NAME = "enterprise_ops_data"

# Ensure collection exists
if not client.collection_exists(collection_name=COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

# 2. Document Extraction Utilities
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def load_raw_data(data_dir):
    documents = []
    for file in os.listdir(data_dir):
        file_path = os.path.join(data_dir, file)
        if file.endswith('.pdf'):
            print(f"Parsing PDF: {file}")
            text = extract_text_from_pdf(file_path)
            documents.append({"text": text, "metadata": {"source": file, "type": "financial"}})
        elif file.endswith('.txt') or file.endswith('.log'):
            print(f"Parsing Logs: {file}")
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            documents.append({"text": text, "metadata": {"source": file, "type": "devops"}})
    return documents

# 3. Processing & Chunking Strategy
# Using Recursive Character Splitting to preserve semantic structure paragraphs/sentences
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,       # Token/Character length window
    chunk_overlap=50,     # Preserves context balance between chunks
    length_function=len
)

raw_docs = load_raw_data("./data")
points = []
point_id = 1

print("Processing text into semantic chunks and generating vectors...")
for doc in raw_docs:
    chunks = text_splitter.split_text(doc["text"])
    for chunk in chunks:
        # Generate 384-dimensional dense vector embedding
        vector = encoder.encode(chunk).tolist()
        
        # Prepare data packet for Vector DB storage
        points.append(
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "page_content": chunk,
                    "source": doc["metadata"]["source"],
                    "data_type": doc["metadata"]["type"]
                }
            )
        )
        point_id += 1

# 4. Storage Upload (Upsert)
if points:
    print(f"Upserting {len(points)} vectors into Qdrant storage...")
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print("Database sync complete!")
else:
    print("No data found to index. Ensure your ./data folder has files.")
