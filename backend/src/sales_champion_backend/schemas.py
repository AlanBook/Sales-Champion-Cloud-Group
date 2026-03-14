from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class UserSummary(ORMModel):
    id: str
    display_name: str
    role_code: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserSummary


class MeResponse(ORMModel):
    id: str
    username: str
    display_name: str
    role_code: str
    store_id: str | None = None


class ProductBase(BaseModel):
    sku_code: str
    name: str
    category: str
    price: Decimal
    price_band: str
    origin: str
    craft: str
    grade_level: str
    taste_profile: list[str] = Field(default_factory=list)
    aroma_profile: list[str] = Field(default_factory=list)
    packaging_level: str
    gift_suitability: str
    self_drink_suitability: str
    business_gift_suitability: str
    description: str
    selling_points: list[str] = Field(default_factory=list)
    taboo_notes: list[str] = Field(default_factory=list)
    is_active: bool = True


class ProductCreate(ProductBase):
    scenes: list[dict[str, Any]] = Field(default_factory=list)


class ProductUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    price: Decimal | None = None
    price_band: str | None = None
    description: str | None = None
    selling_points: list[str] | None = None
    taboo_notes: list[str] | None = None
    packaging_level: str | None = None
    gift_suitability: str | None = None
    self_drink_suitability: str | None = None
    business_gift_suitability: str | None = None


class ProductRead(ProductBase, ORMModel):
    id: str
    created_at: datetime
    updated_at: datetime
    scenes: list[dict[str, Any]] = Field(default_factory=list)


class KnowledgeDocumentBase(BaseModel):
    doc_type: str
    title: str
    source_type: str = "manual"
    source_ref: str | None = None
    summary: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    status: str = "active"


class KnowledgeDocumentCreate(KnowledgeDocumentBase):
    pass


class KnowledgeIngestRequest(BaseModel):
    doc_type: str
    title: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    source_type: str = "manual"
    source_ref: str | None = None


class KnowledgeDocumentRead(ORMModel):
    id: str
    doc_type: str
    title: str
    source_type: str
    source_ref: str | None
    summary: str
    metadata_json: dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime


class KnowledgeSearchItem(BaseModel):
    document_id: str
    chunk_id: str
    doc_type: str
    title: str
    score: float
    content: str
    source_ref: str | None = None


class KnowledgeSearchResponse(BaseModel):
    items: list[KnowledgeSearchItem]


class AssistantInput(BaseModel):
    customer_message: str
    scene_hint: str | None = None
    budget_range: str | None = None
    taste_preference: list[str] = Field(default_factory=list)


class AssistantRecommendRequest(BaseModel):
    staff_id: str
    customer_id: str | None = None
    session_id: str | None = None
    input: AssistantInput


class RecommendedProduct(BaseModel):
    product_id: str
    product_name: str
    fit_score: float
    reason_points: list[str]
    suggested_pitch: str
    risk_notes: list[str]


class ObjectionStrategy(BaseModel):
    type: str
    logic_points: list[str]
    suggested_pitch: str


class SalesAssistantResult(BaseModel):
    customer_intent: str
    scene: str
    budget_range: str
    taste_preference: list[str]
    recommended_products: list[RecommendedProduct]
    recommendation_reasons: list[str]
    objection_strategy: ObjectionStrategy
    suggested_pitch: str
    follow_up_questions: list[str]
    confidence: float
    evidence_sources: list[str]


class AssistantRecommendResponse(BaseModel):
    session_id: str
    result: SalesAssistantResult


class ConversationMessageCreate(BaseModel):
    role: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConversationMessageRead(BaseModel):
    id: str
    role: str
    content: str
    metadata_json: dict[str, Any]
    created_at: datetime


class SessionResponse(BaseModel):
    id: str
    scene: str
    customer_intent: str
    budget_range: str
    taste_preference: list[str]
    status: str
    recommended_product_ids: list[str]
    messages: list[ConversationMessageRead]


class TrainingScenario(BaseModel):
    scene: str
    customer_message: str


class TrainingEvaluateRequest(BaseModel):
    staff_id: str
    scenario: TrainingScenario
    sales_reply: str


class TrainingEvaluateResponse(BaseModel):
    score: int
    dimension_scores: dict[str, int]
    missing_questions: list[str]
    improvement_suggestions: list[str]
    rewritten_reply: str


class OverviewStaffItem(BaseModel):
    staff_id: str
    name: str
    score: float


class FrequencyItem(BaseModel):
    type: str
    count: int


class DashboardOverviewResponse(BaseModel):
    today_reception_count: int
    today_conversion_count: int
    today_revenue: float
    week_reception_count: int
    week_conversion_rate: float
    top_staff: list[OverviewStaffItem]
    top_objections: list[FrequencyItem]


class RankingItem(BaseModel):
    staff_id: str
    name: str
    level: str
    total_score: float
    dimensions: dict[str, float]


class ChampionRankingResponse(BaseModel):
    items: list[RankingItem]


class ChampionDetailResponse(BaseModel):
    staff_id: str
    name: str
    role_level: str
    total_score: float
    dimensions: dict[str, float]
    radar: list[dict[str, float | str]]
    diagnostics: list[str]


class QuestionInsight(BaseModel):
    label: str
    count: int


class ProductInsight(BaseModel):
    product_id: str
    product_name: str
    heat: int
    paid_orders: int
    low_conversion_risk: bool


class TeamWeakness(BaseModel):
    dimension: str
    score: float
    suggestion: str


class ChampionRuleItemPayload(BaseModel):
    dimension_code: str
    dimension_name: str
    weight: float
    config_json: dict[str, Any]


class ChampionRulePayload(BaseModel):
    rule_name: str
    version: str
    total_formula: str
    status: str
    effective_from: date
    effective_to: date | None = None
    items: list[ChampionRuleItemPayload]


class ChampionCalculationRequest(BaseModel):
    rule_id: str
    period_type: str
    period_value: str


class SeedResponse(BaseModel):
    ok: bool
    message: str


class DemoScenario(BaseModel):
    title: str
    customer_input: str
    system_expectation: list[str]
