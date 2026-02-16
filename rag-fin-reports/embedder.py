from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from config import *

client = OpenAI(api_key=OPENAI_API_KEY)

# qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
qdrant = QdrantClient(path="./qdrant_data")

def init_collection():
    qdrant.recreate_collection(
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


def upsert_chunks(chunks):
    points = []

    for idx, chunk in enumerate(chunks):

        embedding_input = f"""
        Company: {chunk['company']}
        Year: {chunk['year']}
        Section: {chunk['section']}
        Page: {chunk['page']}
        Text: {chunk['text']}
        """

        vector = embed_text(embedding_input)

        payload = {
            "company": chunk["company"],
            "year": chunk["year"],
            "section": chunk["section"],
            "page": chunk["page"],
            "text": chunk["text"],
            "entities": chunk.get("entities", {})
        }

        points.append(PointStruct(id=idx, vector=vector, payload=payload))

    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
