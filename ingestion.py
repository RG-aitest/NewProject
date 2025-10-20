import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader

# ============== Load Config ==============
with open("config.json", "r") as f:
    config = json.load(f)

DATA_FOLDER = config["DataFolder"]
VECTOR_DB_PATH = config["VectorDBPath"]
EMBED_MODEL = config["EmbeddingModel"]
CHUNK_SIZE = config["ChunkSize"]
CHUNK_OVERLAP = config["ChunkOverlap"]

# ============== Helper Functions ==============

def load_documents(folder_path):
    docs = []
    for file in os.listdir(folder_path):
        path = os.path.join(folder_path, file)
        if file.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                docs.append(f.read())
        elif file.endswith(".pdf"):
            text = ""
            reader = PdfReader(path)
            for page in reader.pages:
                text += page.extract_text() or ""
            docs.append(text)
    return docs

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# ============== Load and Embed ==============

print("📄 Loading documents...")
documents = load_documents(DATA_FOLDER)

print(f"Found {len(documents)} documents. Splitting into chunks...")
all_chunks = []
for doc in documents:
    all_chunks.extend(chunk_text(doc, CHUNK_SIZE, CHUNK_OVERLAP))

print(f"Total chunks: {len(all_chunks)}")

print("🔍 Loading embedding model...")
model = SentenceTransformer(EMBED_MODEL)

print("⚙️ Generating embeddings...")
embeddings = model.encode(all_chunks, convert_to_numpy=True)

# ============== Save to FAISS ==============

dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

os.makedirs(os.path.dirname(VECTOR_DB_PATH), exist_ok=True)
faiss.write_index(index, VECTOR_DB_PATH)

print(f"✅ Ingestion complete. Saved FAISS index to {VECTOR_DB_PATH}")
print(f"Vector dimension: {dimension}, Total entries: {index.ntotal}")
