"""
rag/rag_pipeline.py – RAG pipeline using ChromaDB vector store + IBM Granite.
Documents sourced from trusted government/banking portals.
"""
from __future__ import annotations

import hashlib
import logging
import os
import re
import time
from typing import Dict, List, Optional, Tuple

import config
from monitoring.rag_monitor import RAGContext, save_rag_event, track_rag
from rag.knowledge_base import KNOWLEDGE_BASE, SOURCE_REGISTRY

logger = logging.getLogger("finsaakhi.rag")

# ── Trusted source domains ─────────────────────────────────────────────────────
TRUSTED_SOURCES = set(SOURCE_REGISTRY.keys()) | {
    "gov.in", "india.gov.in", "paisabazaar.com", "bankbazaar.com",
}


# ── ChromaDB vector store ──────────────────────────────────────────────────────
_chroma_client = None
_collection = None


def _get_collection():
    global _chroma_client, _collection
    if _collection is not None:
        return _collection
    try:
        import chromadb
        from chromadb.utils import embedding_functions
        _chroma_client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
        emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        _collection = _chroma_client.get_or_create_collection(
            name="finsaakhi_kb",
            embedding_function=emb_fn,
            metadata={"hnsw:space": "cosine"},
        )
        # Seed knowledge base if empty
        if _collection.count() == 0:
            _seed_knowledge_base()
        return _collection
    except Exception as exc:
        logger.error("ChromaDB init failed: %s", exc)
        return None


def _seed_knowledge_base():
    """Populate ChromaDB with the built-in knowledge base."""
    col = _collection
    ids = [doc["id"] for doc in KNOWLEDGE_BASE]
    docs = [doc["content"] for doc in KNOWLEDGE_BASE]
    metas = [
        {
            "source": doc["source"],
            "category": doc.get("module", doc.get("category", "general")),
            "language": doc["language"],
            "source_date": doc.get("source_date", ""),
        }
        for doc in KNOWLEDGE_BASE
    ]
    col.add(documents=docs, ids=ids, metadatas=metas)
    logger.info("Seeded knowledge base with %d documents.", len(KNOWLEDGE_BASE))


def _validate_document(doc_text: str, source: str) -> bool:
    """Check that a retrieved document does not contain injection patterns."""
    injection_re = re.compile(
        r"ignore\s+(?:all\s+)?(?:previous|above)\s+instruction|"
        r"you\s+are\s+now\s+a|system\s*:\s*\[", re.I
    )
    if injection_re.search(doc_text):
        from monitoring.guardrail_monitor import log_rag_guardrail
        log_rag_guardrail("document_injection_detected", "critical")
        return False
    # Freshness: reject documents flagged explicitly stale (placeholder – real impl would check date metadata)
    return True


def retrieve(
    query: str,
    language: str = "en",
    n_results: int = None,
    request_id: str = None,
) -> Tuple[List[Dict], RAGContext]:
    """
    Retrieve relevant documents for query.
    Returns (docs_list, rag_context) for monitoring.
    """
    n_results = n_results or config.RAG_MAX_DOCS
    ctx = RAGContext(request_id=request_id, language=language)
    ctx.start()

    try:
        col = _get_collection()
        if col is None:
            ctx.finish(success=False)
            ctx.empty_retrieval = True
            save_rag_event(ctx)
            # Fallback to in-memory keyword search
            return _keyword_fallback(query, language, n_results), ctx

        results = col.query(
            query_texts=[query],
            n_results=min(n_results, col.count() or 1),
            where={"language": language} if language != "en" else None,
        )
        docs_out = []
        distances = results.get("distances", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        for i, (doc_text, meta, dist) in enumerate(zip(documents, metadatas, distances)):
            relevance = 1.0 - dist  # cosine distance to similarity
            source = meta.get("source", "unknown")
            if relevance < config.RAG_RELEVANCE_THRESHOLD:
                continue
            if not _validate_document(doc_text, source):
                ctx.doc_validation_failed = True
                continue
            docs_out.append({
                "content": doc_text,
                "source": source,
                "category": meta.get("category", "general"),
                "relevance": round(relevance, 4),
                "source_date": meta.get("source_date", ""),
            })

        ctx.documents_retrieved = len(docs_out)
        ctx.relevance_score = (
            sum(d["relevance"] for d in docs_out) / len(docs_out) if docs_out else 0.0
        )
        ctx.sources_cited = len({d["source"] for d in docs_out})
        ctx.grounded = len(docs_out) > 0
        ctx.finish(success=True)

        if not docs_out:
            # Try keyword fallback
            docs_out = _keyword_fallback(query, language, n_results)
            ctx.documents_retrieved = len(docs_out)

        save_rag_event(ctx)
        return docs_out, ctx

    except Exception as exc:
        ctx.finish(success=False)
        save_rag_event(ctx)
        logger.error("RAG retrieval error: %s", exc)
        return _keyword_fallback(query, language, n_results), ctx


def _keyword_fallback(query: str, language: str, n: int) -> List[Dict]:
    """Simple keyword matching fallback when vector DB unavailable."""
    q_lower = query.lower()
    scored = []
    for doc in KNOWLEDGE_BASE:
        if doc["language"] not in (language, "en"):
            continue
        words = set(doc["content"].lower().split())
        q_words = set(q_lower.split())
        overlap = len(words & q_words)
        if overlap > 0:
            scored.append((overlap, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for _, doc in scored[:n]:
        results.append({
            "content": doc["content"],
            "source": doc["source"],
            "category": doc.get("module", doc.get("category", "general")),
            "relevance": 0.5,
            "source_date": doc.get("source_date", ""),
        })
    return results


def format_context(docs: List[Dict]) -> str:
    """Format retrieved docs as context string for LLM prompt."""
    if not docs:
        return ""
    parts = []
    for i, doc in enumerate(docs, 1):
        date_info = f" ({doc['source_date']})" if doc.get("source_date") else ""
        parts.append(f"[Source {i}: {doc['source']}{date_info}]\n{doc['content']}")
    return "\n\n".join(parts)


def get_source_info(source_domain: str) -> dict:
    """Return display info for a source domain."""
    from rag.knowledge_base import SOURCE_REGISTRY
    return SOURCE_REGISTRY.get(source_domain, {
        "name": source_domain, "url": f"https://{source_domain}", "category": "General"
    })
