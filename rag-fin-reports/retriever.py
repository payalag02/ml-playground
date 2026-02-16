import re
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny
from openai import OpenAI
from config import *

client = OpenAI(api_key=OPENAI_API_KEY)
# qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
qdrant = QdrantClient(path="./qdrant_data")

COLLECTION = COLLECTION_NAME


def embed_query(query):
    """Generate an embedding vector for the given text using OpenAI."""
    emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    return emb.data[0].embedding


def search_chunks(query, companies=None, year=None, top_k=6):
    """Retrieve the most relevant chunks from Qdrant for the given query.

    For multi-company queries (e.g. "Compare Wipro with Infosys"), each
    company is searched independently with a cleaned-up, single-company
    version of the query.  This prevents one company's results from
    dominating because the shared embedding happened to be closer to
    that company's data.
    """

    vector = embed_query(query)

    # --- Multi-company path ---
    # Search each company separately so every company gets equal
    # representation in the retrieved context.
    if companies and len(companies) > 1:
        per_company_k = top_k
        all_results = []

        for company in companies:
            # Build a single-company query by stripping out the names of
            # all *other* companies and any leftover comparison words
            # (e.g. "compared to", "vs").  The resulting query is close
            # to what the user would write when asking about one company,
            # so the embedding aligns well with that company's chunks.
            other_companies = [c for c in companies if c != company]
            focused_query = re.sub(
                r'\s*\b(?:' + '|'.join(re.escape(c) for c in other_companies) + r')\b\s*',
                ' ',
                query,
                flags=re.IGNORECASE
            ).strip()
            focused_query = re.sub(
                r'\s*(compared to|versus|vs\.?|and)\s*', ' ',
                focused_query,
                flags=re.IGNORECASE
            ).strip()
            focused_vector = embed_query(focused_query)

            # Apply metadata filters for company (and optionally year)
            conditions = [
                FieldCondition(
                    key="company",
                    match=MatchValue(value=company)
                )
            ]
            if year:
                conditions.append(
                    FieldCondition(
                        key="year",
                        match=MatchValue(value=year)
                    )
                )

            results = qdrant.query_points(
                collection_name=COLLECTION,
                query=focused_vector,
                limit=per_company_k,
                query_filter=Filter(must=conditions),
                with_payload=True
            )
            all_results.extend(results.points)

        # Rank all collected chunks by relevance score
        all_results.sort(key=lambda x: x.score, reverse=True)

        return [p.payload for p in all_results]

    # --- Single-company / unfiltered path ---
    conditions = []

    if companies:
        conditions.append(
            FieldCondition(
                key="company",
                match=MatchValue(value=companies[0])
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

    return [p.payload for p in results.points]
