from __future__ import annotations

import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from sales_champion_backend.db.models import (
    ConversationMessage,
    ConversationSession,
    Customer,
    FollowUpEvent,
    ObjectionCase,
    ObjectionEvent,
    RecommendationEvent,
    User,
)
from sales_champion_backend.schemas import (
    AssistantRecommendRequest,
    AssistantRecommendResponse,
    ObjectionStrategy,
    RecommendedProduct,
    SalesAssistantResult,
)
from sales_champion_backend.services.retrieval_service import search_knowledge, search_products

SCENE_KEYWORDS = {
    "gift_leader": ["送领导", "领导", "体面"],
    "gift_elder": ["长辈", "父母", "长者"],
    "business_visit": ["商务", "客户", "拜访", "商务礼赠"],
    "beginner_help": ["不懂茶", "不太懂", "不容易出错"],
    "self_drink": ["自己喝", "自饮", "平时喝"],
}

TASTE_KEYWORDS = {
    "清香": ["清一点", "清香", "轻口感"],
    "醇厚": ["醇", "厚", "回甘"],
    "花香": ["花香"],
    "焙火": ["焙火", "岩茶"],
}


def detect_scene(message: str, hint: str | None) -> tuple[str, str]:
    if hint:
        if hint in {"gift_leader", "gift_elder", "business_visit", "beginner_help", "self_drink"}:
            if hint == "gift_leader" or hint == "gift_elder":
                return hint, "gift"
            if hint == "business_visit":
                return hint, "business_gift"
            if hint == "beginner_help":
                return hint, "beginner_help"
            return hint, "self_drink"
    for scene, keywords in SCENE_KEYWORDS.items():
        if any(keyword in message for keyword in keywords):
            if scene in {"gift_leader", "gift_elder"}:
                return scene, "gift"
            if scene == "business_visit":
                return scene, "business_gift"
            if scene == "beginner_help":
                return scene, "beginner_help"
            return scene, "self_drink"
    if "贵" in message:
        return "self_drink", "price_question"
    return "self_drink", "self_drink"


def detect_budget(message: str, budget_hint: str | None) -> str:
    if budget_hint:
        return budget_hint
    digits = [int(item) for item in re.findall(r"(\d{2,4})", message)]
    if not digits:
        return "500-1500"
    budget = max(digits)
    if budget <= 500:
        return "0-500"
    if budget <= 1500:
        return "500-1500"
    if budget <= 3000:
        return "1500-3000"
    return "3000+"


def detect_tastes(message: str, taste_hint: list[str]) -> list[str]:
    if taste_hint:
        return taste_hint
    tastes = [label for label, keywords in TASTE_KEYWORDS.items() if any(k in message for k in keywords)]
    return tastes or ["清香"]


def _build_objection_strategy(db: Session, message: str) -> ObjectionStrategy:
    objection_type = "price_high" if "贵" in message else "gift_unsure" if "送礼" in message else "dont_understand_tea"
    case = db.scalar(
        select(ObjectionCase).where(ObjectionCase.objection_type == objection_type)
    )
    if case:
        return ObjectionStrategy(
            type=objection_type,
            logic_points=case.handling_logic[:3],
            suggested_pitch=case.suggested_pitch,
        )
    return ObjectionStrategy(
        type=objection_type,
        logic_points=["先确认场景", "解释价值", "控制风险"],
        suggested_pitch="先帮客户把使用场景说清楚，再解释为什么这个价格更稳妥。",
    )


def _follow_up_questions(scene: str) -> list[str]:
    mapping = {
        "self_drink": ["更偏白茶、岩茶还是绿茶口感？", "平时自己喝更看重清香还是回甘？"],
        "gift_leader": ["更在意包装体面还是茶本身品质？", "收礼人平时偏传统口感还是清雅口感？"],
        "gift_elder": ["长辈平时喝红茶、白茶还是熟普更多？", "更看重温和顺口还是有陈香层次？"],
        "business_visit": ["这次更偏商务礼赠还是客户维护？", "客户对品牌体面度要求高不高？"],
        "beginner_help": ["这次主要是自己喝还是送礼？", "更能接受清香、花香还是更醇一点的口感？"],
    }
    return mapping.get(scene, ["客户更重视口感还是包装？"])


def recommend(db: Session, payload: AssistantRecommendRequest) -> AssistantRecommendResponse:
    scene, customer_intent = detect_scene(
        payload.input.customer_message, payload.input.scene_hint
    )
    budget_range = detect_budget(payload.input.customer_message, payload.input.budget_range)
    tastes = detect_tastes(payload.input.customer_message, payload.input.taste_preference)
    ranked_products = search_products(
        db,
        scene=scene,
        budget_range=budget_range,
        taste_preference=tastes,
        keyword=payload.input.customer_message,
    )
    knowledge_hits = search_knowledge(
        db,
        payload.input.customer_message,
        top_k=4,
    )
    recommended_products = [
        RecommendedProduct(
            product_id=item["product"].id,
            product_name=item["product"].name,
            fit_score=item["fit_score"],
            reason_points=item["reasons"][:3],
            suggested_pitch=(
                f"这款{item['product'].name}更适合当前场景，"
                f"重点可以讲{item['reasons'][0]}。"
            ),
            risk_notes=item["product"].taboo_notes[:2] or ["若客户更看重收藏属性，可上探更高档款。"],
        )
        for item in ranked_products
    ]
    evidence_sources = [
        f"product:{item.product_id}" for item in recommended_products
    ] + [
        f"{hit.doc_type}:{hit.source_ref or hit.document_id}" for hit in knowledge_hits
    ]
    objection_strategy = _build_objection_strategy(db, payload.input.customer_message)
    recommendation_reasons = [
        f"当前属于{scene}场景，优先考虑预算、包装和稳定成交。",
        "推荐同时参考了商品适配度、知识库 FAQ 和销冠话术案例。",
    ]
    suggested_pitch = (
        f"如果按{scene}这个场景来选，我建议先从{recommended_products[0].product_name if recommended_products else '稳妥款'}切入，"
        "先讲场景适配，再讲口感和价值，不要先堆专业术语。"
    )
    result = SalesAssistantResult(
        customer_intent=customer_intent,
        scene=scene,
        budget_range=budget_range,
        taste_preference=tastes,
        recommended_products=recommended_products,
        recommendation_reasons=recommendation_reasons,
        objection_strategy=objection_strategy,
        suggested_pitch=suggested_pitch,
        follow_up_questions=_follow_up_questions(scene),
        confidence=round(0.74 + min(len(recommended_products), 3) * 0.07, 2),
        evidence_sources=list(dict.fromkeys(evidence_sources)),
    )

    customer = None
    if payload.customer_id:
        customer = db.get(Customer, payload.customer_id)
    if not customer:
        customer = Customer(
            source_channel="in_store",
            customer_segment="礼赠客" if scene.startswith("gift") else "新客",
            preference_tags=tastes,
            notes=payload.input.customer_message,
        )
        db.add(customer)
        db.flush()

    session = None
    if payload.session_id:
        session = db.get(ConversationSession, payload.session_id)
    if not session:
        session = ConversationSession(
            staff_id=payload.staff_id,
            customer_id=customer.id,
            channel="in_store",
            scene=scene,
            customer_intent=customer_intent,
            budget_range=budget_range,
            taste_preference=tastes,
            status="open",
            recommended_product_ids=[item.product_id for item in recommended_products],
            conversion_result="pending",
        )
        db.add(session)
        db.flush()
    else:
        session.scene = scene
        session.customer_intent = customer_intent
        session.budget_range = budget_range
        session.taste_preference = tastes
        session.recommended_product_ids = [item.product_id for item in recommended_products]

    db.add(
        ConversationMessage(
            session_id=session.id,
            role="customer",
            content=payload.input.customer_message,
            metadata_json={"scene_hint": payload.input.scene_hint},
        )
    )
    db.add(
        ConversationMessage(
            session_id=session.id,
            role="assistant",
            content=result.suggested_pitch,
            metadata_json=result.model_dump(),
        )
    )
    db.add(
        RecommendationEvent(
            session_id=session.id,
            staff_id=payload.staff_id,
            recommended_products=[item.model_dump() for item in recommended_products],
            recommendation_reasons=result.recommendation_reasons,
            confidence=result.confidence,
            evidence_sources=result.evidence_sources,
        )
    )
    db.add(
        FollowUpEvent(
            session_id=session.id,
            suggested_questions=result.follow_up_questions,
            chosen_action=None,
        )
    )
    if objection_strategy.type == "price_high" or "贵" in payload.input.customer_message:
        db.add(
            ObjectionEvent(
                session_id=session.id,
                objection_type="price_high",
                customer_quote=payload.input.customer_message,
                resolution_status="handled",
            )
        )
    db.flush()
    return AssistantRecommendResponse(session_id=session.id, result=result)


def create_session(db: Session, staff_id: str) -> ConversationSession:
    staff = db.get(User, staff_id)
    if not staff:
        raise ValueError("导购不存在。")
    session = ConversationSession(
        staff_id=staff_id,
        customer_id=None,
        channel="in_store",
        scene="self_drink",
        customer_intent="self_drink",
        budget_range="500-1500",
        taste_preference=[],
        status="open",
        recommended_product_ids=[],
        conversion_result="pending",
    )
    db.add(session)
    db.flush()
    return session


def get_session_detail(db: Session, session_id: str) -> dict[str, Any]:
    session = db.get(ConversationSession, session_id)
    if not session:
        raise ValueError("会话不存在。")
    messages = db.scalars(
        select(ConversationMessage).where(ConversationMessage.session_id == session_id)
    ).all()
    return {
        "id": session.id,
        "scene": session.scene,
        "customer_intent": session.customer_intent,
        "budget_range": session.budget_range,
        "taste_preference": session.taste_preference,
        "status": session.status,
        "recommended_product_ids": session.recommended_product_ids,
        "messages": messages,
    }


def append_message(
    db: Session, session_id: str, role: str, content: str, metadata: dict[str, Any]
) -> ConversationMessage:
    session = db.get(ConversationSession, session_id)
    if not session:
        raise ValueError("会话不存在。")
    message = ConversationMessage(
        session_id=session_id,
        role=role,
        content=content,
        metadata_json=metadata,
    )
    db.add(message)
    db.flush()
    return message
