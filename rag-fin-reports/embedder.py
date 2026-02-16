import uuid
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from config import *

client = OpenAI(api_key=OPENAI_API_KEY)

# qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
qdrant = QdrantClient(path="./qdrant_data")

def init_collection():
    existing = [c.name for c in qdrant.get_collections().collections]

    if COLLECTION_NAME not in existing:
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=1536,
                distance=Distance.COSINE
            )
        )

def embed_text(text):
    emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return emb.data[0].embedding

def batch_embed(texts, batch_size=64):
    vectors = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        resp = client.embeddings.create(
            model="text-embedding-3-small",
            input=batch
        )

        vectors.extend([d.embedding for d in resp.data])

    return vectors


def upsert_chunks(chunks):

    print(f"Total chunks to embed: {len(chunks)}")

    # 🔥 Build embedding inputs first
    embedding_inputs = [
        f"""
            Company: {chunk['company']}
            Year: {chunk['year']}
            Section: {chunk['section']}
            Page: {chunk['page']}
            Text: {chunk['text']}
"""
        for chunk in chunks
    ]

    print("Generating embeddings in batches...")
    vectors = batch_embed(embedding_inputs, batch_size=64)

    print("Building Qdrant points...")
    points = []

    for idx, chunk in enumerate(chunks):

        payload = {
            "company": chunk["company"],
            "year": chunk["year"],
            "section": chunk["section"],
            "page": chunk["page"],
            "text": chunk["text"],
            "entities": chunk.get("entities", {})
        }

        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vectors[idx],
                payload=payload
            )
        )

    print("Upserting into Qdrant...")
    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    print("✅ Upsert complete")
