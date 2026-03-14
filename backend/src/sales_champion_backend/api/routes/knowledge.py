from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select

from sales_champion_backend.api.deps import DBSession, get_current_user, require_roles
from sales_champion_backend.db.models import KnowledgeDocument, User
from sales_champion_backend.schemas import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentRead,
    KnowledgeIngestRequest,
    KnowledgeSearchResponse,
)
from sales_champion_backend.services.retrieval_service import ingest_document, search_knowledge

router = APIRouter()


@router.get("/documents", response_model=list[KnowledgeDocumentRead])
def list_documents(
    db: DBSession,
    _: Annotated[User, Depends(get_current_user)],
    doc_type: str | None = None,
    status: str | None = None,
    keyword: str | None = None,
) -> list[KnowledgeDocument]:
    statement = select(KnowledgeDocument)
    if doc_type:
        statement = statement.where(KnowledgeDocument.doc_type == doc_type)
    if status:
        statement = statement.where(KnowledgeDocument.status == status)
    if keyword:
        statement = statement.where(KnowledgeDocument.title.contains(keyword))
    return db.scalars(statement.order_by(KnowledgeDocument.created_at.desc())).all()


@router.post("/documents", response_model=KnowledgeDocumentRead)
def create_document(
    payload: KnowledgeDocumentCreate,
    db: DBSession,
    _: Annotated[User, Depends(require_roles("admin", "manager", "boss"))],
) -> KnowledgeDocument:
    document = KnowledgeDocument(
        doc_type=payload.doc_type,
        title=payload.title,
        source_type=payload.source_type,
        source_ref=payload.source_ref,
        summary=payload.summary,
        metadata_json=payload.metadata,
        status=payload.status,
    )
    db.add(document)
    db.flush()
    return document


@router.post("/ingest", response_model=KnowledgeDocumentRead)
def ingest(
    payload: KnowledgeIngestRequest,
    db: DBSession,
    _: Annotated[User, Depends(require_roles("admin", "manager", "boss"))],
) -> KnowledgeDocument:
    return ingest_document(db, payload)


@router.get("/search", response_model=KnowledgeSearchResponse)
def search(
    db: DBSession,
    _: Annotated[User, Depends(get_current_user)],
    q: str,
    top_k: int = 5,
    doc_type: str | None = None,
) -> KnowledgeSearchResponse:
    return KnowledgeSearchResponse(items=search_knowledge(db, q, top_k=top_k, doc_type=doc_type))
