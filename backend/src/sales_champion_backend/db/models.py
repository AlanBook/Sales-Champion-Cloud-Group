from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import uuid4

# 临时禁用 pgvector 以支持 SQLite
# from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from sales_champion_backend.db.session import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return str(uuid4())


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )


class Role(Base):
    __tablename__ = "roles"

    code: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class Store(Base, TimestampMixin):
    __tablename__ = "stores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    city: Mapped[str] = mapped_column(String(64), nullable=False)
    region: Mapped[str] = mapped_column(String(64), nullable=False)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(64), nullable=False)
    email: Mapped[str | None] = mapped_column(String(128))
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role_code: Mapped[str] = mapped_column(ForeignKey("roles.code"), nullable=False)
    store_id: Mapped[str | None] = mapped_column(ForeignKey("stores.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class StaffProfile(Base, TimestampMixin):
    __tablename__ = "staff_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    hire_date: Mapped[date | None] = mapped_column(Date)
    level: Mapped[str] = mapped_column(String(32), nullable=False)
    specialty_tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    sku_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    price_band: Mapped[str] = mapped_column(String(32), nullable=False)
    origin: Mapped[str] = mapped_column(String(128), nullable=False)
    craft: Mapped[str] = mapped_column(String(128), nullable=False)
    grade_level: Mapped[str] = mapped_column(String(64), nullable=False)
    taste_profile: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    aroma_profile: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    packaging_level: Mapped[str] = mapped_column(String(64), nullable=False)
    gift_suitability: Mapped[str] = mapped_column(String(64), nullable=False)
    self_drink_suitability: Mapped[str] = mapped_column(String(64), nullable=False)
    business_gift_suitability: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    selling_points: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    taboo_notes: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ProductTag(Base):
    __tablename__ = "product_tags"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tag_type: Mapped[str] = mapped_column(String(32), nullable=False)
    tag_code: Mapped[str] = mapped_column(String(64), nullable=False)
    tag_name: Mapped[str] = mapped_column(String(64), nullable=False)


class ProductTagRelation(Base):
    __tablename__ = "product_tag_relations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    tag_id: Mapped[str] = mapped_column(ForeignKey("product_tags.id"), nullable=False)


class ProductScene(Base):
    __tablename__ = "product_scenes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    scene_code: Mapped[str] = mapped_column(String(64), nullable=False)
    fit_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)


class KnowledgeDocument(Base, TimestampMixin):
    __tablename__ = "knowledge_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    doc_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_ref: Mapped[str | None] = mapped_column(String(128))
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    document_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_documents.id"), nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(JSON, default=list, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)


class FAQItem(Base, TimestampMixin):
    __tablename__ = "faq_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    related_product_id: Mapped[str | None] = mapped_column(ForeignKey("products.id"))
    scene_code: Mapped[str | None] = mapped_column(String(64))
    document_id: Mapped[str | None] = mapped_column(ForeignKey("knowledge_documents.id"))


class SalesPlaybook(Base, TimestampMixin):
    __tablename__ = "sales_playbooks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    scene_code: Mapped[str] = mapped_column(String(64), nullable=False)
    objection_type: Mapped[str | None] = mapped_column(String(64))
    template_text: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)


class ObjectionCase(Base, TimestampMixin):
    __tablename__ = "objection_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    objection_type: Mapped[str] = mapped_column(String(64), nullable=False)
    customer_quote: Mapped[str] = mapped_column(Text, nullable=False)
    handling_logic: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    suggested_pitch: Mapped[str] = mapped_column(Text, nullable=False)
    risk_notes: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    document_id: Mapped[str | None] = mapped_column(ForeignKey("knowledge_documents.id"))


class ChampionCase(Base, TimestampMixin):
    __tablename__ = "champion_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    scene_code: Mapped[str] = mapped_column(String(64), nullable=False)
    customer_profile: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    highlights: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    transcript: Mapped[str] = mapped_column(Text, nullable=False)
    key_patterns: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    document_id: Mapped[str | None] = mapped_column(ForeignKey("knowledge_documents.id"))


class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    source_channel: Mapped[str] = mapped_column(String(32), nullable=False)
    customer_segment: Mapped[str] = mapped_column(String(64), nullable=False)
    preference_tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class ConversationSession(Base, TimestampMixin):
    __tablename__ = "conversation_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    staff_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    customer_id: Mapped[str | None] = mapped_column(ForeignKey("customers.id"))
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    scene: Mapped[str] = mapped_column(String(64), nullable=False)
    customer_intent: Mapped[str] = mapped_column(String(64), nullable=False)
    budget_range: Mapped[str] = mapped_column(String(64), nullable=False)
    taste_preference: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="open", nullable=False)
    recommended_product_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    conversion_result: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("conversation_sessions.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )


class RecommendationEvent(Base):
    __tablename__ = "recommendation_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("conversation_sessions.id"), nullable=False
    )
    staff_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    recommended_products: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, default=list, nullable=False
    )
    recommendation_reasons: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    evidence_sources: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )


class ObjectionEvent(Base):
    __tablename__ = "objection_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("conversation_sessions.id"), nullable=False
    )
    objection_type: Mapped[str] = mapped_column(String(64), nullable=False)
    customer_quote: Mapped[str] = mapped_column(Text, nullable=False)
    resolution_status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )


class FollowUpEvent(Base):
    __tablename__ = "followup_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("conversation_sessions.id"), nullable=False
    )
    suggested_questions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    chosen_action: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    session_id: Mapped[str | None] = mapped_column(ForeignKey("conversation_sessions.id"))
    staff_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    order_status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )


class StaffDailyMetric(Base):
    __tablename__ = "staff_daily_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    staff_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    metric_date: Mapped[date] = mapped_column(Date, nullable=False)
    reception_count: Mapped[int] = mapped_column(Integer, nullable=False)
    recommendation_count: Mapped[int] = mapped_column(Integer, nullable=False)
    conversion_count: Mapped[int] = mapped_column(Integer, nullable=False)
    conversion_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    avg_order_value: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    objection_resolved_count: Mapped[int] = mapped_column(Integer, nullable=False)
    high_price_objection_count: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class ChampionScoreRule(Base):
    __tablename__ = "champion_score_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    rule_name: Mapped[str] = mapped_column(String(128), nullable=False)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    total_formula: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )


class ChampionScoreRuleItem(Base):
    __tablename__ = "champion_score_rule_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    rule_id: Mapped[str] = mapped_column(
        ForeignKey("champion_score_rules.id"), nullable=False
    )
    dimension_code: Mapped[str] = mapped_column(String(64), nullable=False)
    dimension_name: Mapped[str] = mapped_column(String(64), nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    config_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


class ChampionScoreSnapshot(Base):
    __tablename__ = "champion_score_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    rule_id: Mapped[str] = mapped_column(
        ForeignKey("champion_score_rules.id"), nullable=False
    )
    staff_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    period_type: Mapped[str] = mapped_column(String(32), nullable=False)
    period_value: Mapped[str] = mapped_column(String(32), nullable=False)
    total_score: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    dimension_scores: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    diagnostic_notes: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )


class TeamInsightSnapshot(Base):
    __tablename__ = "team_insight_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    period_type: Mapped[str] = mapped_column(String(32), nullable=False)
    period_value: Mapped[str] = mapped_column(String(32), nullable=False)
    snapshot_type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
