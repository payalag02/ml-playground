from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from openai import OpenAI
from config import *

client = OpenAI(api_key=OPENAI_API_KEY)
# qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
qdrant = QdrantClient(path="./qdrant_data")

COLLECTION = COLLECTION_NAME


def embed_query(query):
    emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    return emb.data[0].embedding


def search_chunks(query, company=None, year=None, top_k=6):

    vector = embed_query(query)
    conditions = []

    if company:
        conditions.append(
            FieldCondition(
                key="company",
                match=MatchValue(value=company)
            )
        )

    if year:
        conditions.append(
            FieldCondition(
                key="year",
                match=MatchValue(value=year)
            )
        )

    query_filter = Filter(must=conditions) if conditions else None

    results = qdrant.query_points(
            collection_name=COLLECTION,
            query=vector,
            limit=top_k,
            query_filter=query_filter,
            with_payload=True
        )
    
    qdrant.close()

    return [p.payload for p in results.points]
