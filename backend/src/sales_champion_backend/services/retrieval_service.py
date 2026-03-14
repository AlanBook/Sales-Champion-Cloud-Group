from __future__ import annotations

import hashlib
import math
import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from sales_champion_backend.core.config import get_settings
from sales_champion_backend.db.models import (
    KnowledgeChunk,
    KnowledgeDocument,
    Product,
    ProductScene,
)
from sales_champion_backend.schemas import KnowledgeIngestRequest, KnowledgeSearchItem


def tokenize(text: str) -> list[str]:
    return re.findall(r"[\u4e00-\u9fffA-Za-z0-9]+", text.lower())


def embed_text(text: str, dimensions: int | None = None) -> list[float]:
    dims = dimensions or get_settings().embedding_dimensions
    vector = [0.0] * dims
    tokens = tokenize(text)
    if not tokens:
      return vector
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        slot = int(digest[:8], 16) % dims
        vector[slot] += 1.0
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [round(value / norm, 6) for value in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    return float(sum(a * b for a, b in zip(left, right)))


def chunk_text(text: str, size: int = 180, overlap: int = 36) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    if len(normalized) <= size:
        return [normalized]
    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = start + size
        chunks.append(normalized[start:end])
        if end >= len(normalized):
            break
        start = max(end - overlap, start + 1)
    return chunks


def ingest_document(db: Session, payload: KnowledgeIngestRequest) -> KnowledgeDocument:
    summary = payload.content[:120].strip()
    document = KnowledgeDocument(
        doc_type=payload.doc_type,
        title=payload.title,
        source_type=payload.source_type,
        source_ref=payload.source_ref,
        summary=summary,
        metadata_json=payload.metadata,
        status="active",
    )
    db.add(document)
    db.flush()

    for index, chunk in enumerate(chunk_text(payload.content)):
        db.add(
            KnowledgeChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk,
                embedding=embed_text(chunk),
                metadata_json=payload.metadata,
            )
        )
    db.flush()
    return document


def search_knowledge(
    db: Session,
    query: str,
    *,
    top_k: int = 5,
    doc_type: str | None = None,
) -> list[KnowledgeSearchItem]:
    statement = select(KnowledgeChunk, KnowledgeDocument).join(
        KnowledgeDocument, KnowledgeChunk.document_id == KnowledgeDocument.id
    )
    if doc_type:
        statement = statement.where(KnowledgeDocument.doc_type == doc_type)
    rows = db.execute(statement).all()
    query_embedding = embed_text(query)
    items: list[KnowledgeSearchItem] = []
    for chunk, document in rows:
        score = cosine_similarity(list(chunk.embedding), query_embedding)
        if score <= 0:
            continue
        items.append(
            KnowledgeSearchItem(
                document_id=document.id,
                chunk_id=chunk.id,
                doc_type=document.doc_type,
                title=document.title,
                score=round(score, 4),
                content=chunk.content,
                source_ref=document.source_ref,
            )
        )
    return sorted(items, key=lambda item: item.score, reverse=True)[:top_k]


def search_products(
    db: Session,
    *,
    scene: str,
    budget_range: str,
    taste_preference: list[str],
    keyword: str,
    top_k: int = 3,
) -> list[dict[str, Any]]:
    products = db.scalars(select(Product).where(Product.is_active.is_(True))).all()
    scenes = db.scalars(select(ProductScene)).all()
    scene_map: dict[str, list[ProductScene]] = {}
    for item in scenes:
        scene_map.setdefault(item.product_id, []).append(item)

    items: list[dict[str, Any]] = []
    for product in products:
        score = 0.25
        reasons: list[str] = []
        for product_scene in scene_map.get(product.id, []):
            if product_scene.scene_code == scene:
                score += float(product_scene.fit_score) / 100
                reasons.append(product_scene.reason)
        if budget_range and budget_range == product.price_band:
            score += 0.28
            reasons.append("预算与商品价格带匹配")
        elif budget_range and budget_range.startswith("0-500") and float(product.price) <= 500:
            score += 0.18
        elif budget_range and budget_range.endswith("+") and float(product.price) >= 3000:
            score += 0.18
        taste_hits = sorted(set(taste_preference) & set(product.taste_profile))
        if taste_hits:
            score += 0.18
            reasons.append(f"口感偏好命中：{' / '.join(taste_hits)}")
        keyword_hits = [word for word in tokenize(keyword) if word in product.description]
        if keyword_hits:
            score += 0.08
        items.append(
            {
                "product": product,
                "fit_score": round(min(score, 0.98), 2),
                "reasons": list(dict.fromkeys(reasons + product.selling_points[:2])),
            }
        )
    return sorted(items, key=lambda item: item["fit_score"], reverse=True)[:top_k]
