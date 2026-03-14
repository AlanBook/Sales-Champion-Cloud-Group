from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from sales_champion_backend.db.models import (
    ConversationMessage,
    ConversationSession,
    ObjectionEvent,
    Order,
    Product,
    RecommendationEvent,
)
from sales_champion_backend.services.champion_service import get_ranking


def _top_staff_overview_items(ranking: list[dict]) -> list[dict]:
    return [
        {
            "staff_id": item["staff_id"],
            "name": item["name"],
            "score": float(item["total_score"]),
        }
        for item in ranking[:5]
    ]


def dashboard_overview(db: Session) -> dict:
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    sessions = db.scalars(select(ConversationSession)).all()
    orders = db.scalars(select(Order).where(Order.order_status == "paid")).all()
    objections = db.scalars(select(ObjectionEvent)).all()
    ranking = get_ranking(db)

    today_sessions = [item for item in sessions if item.created_at.date() == today]
    week_sessions = [item for item in sessions if item.created_at.date() >= week_start]
    today_orders = [item for item in orders if item.created_at.date() == today]
    week_converted = [item for item in week_sessions if item.conversion_result == "converted"]
    objection_counter = Counter(item.objection_type for item in objections)
    return {
        "today_reception_count": len(today_sessions),
        "today_conversion_count": len(today_orders),
        "today_revenue": round(sum(float(item.amount) for item in today_orders), 2),
        "week_reception_count": len(week_sessions),
        "week_conversion_rate": round(
            len(week_converted) / len(week_sessions), 2
        )
        if week_sessions
        else 0.0,
        "top_staff": _top_staff_overview_items(ranking),
        "top_objections": [
            {"type": objection_type, "count": count}
            for objection_type, count in objection_counter.most_common(5)
        ],
    }


def top_questions(db: Session) -> list[dict]:
    messages = db.scalars(
        select(ConversationMessage).where(ConversationMessage.role.in_(["customer", "user"]))
    ).all()
    labels = []
    for message in messages:
        content = message.content
        if "送领导" in content or "领导" in content:
            labels.append("送领导怎么选")
        elif "长辈" in content:
            labels.append("送长辈怎么选")
        elif "贵" in content:
            labels.append("为什么这么贵")
        elif "不懂茶" in content:
            labels.append("不懂茶怎么选")
        elif "自己喝" in content or "自饮" in content:
            labels.append("自己喝选哪款")
        else:
            labels.append("预算怎么配")
    counter = Counter(labels)
    return [{"label": label, "count": count} for label, count in counter.most_common(8)]


def top_objections(db: Session) -> list[dict]:
    counter = Counter(
        item.objection_type for item in db.scalars(select(ObjectionEvent)).all()
    )
    return [{"type": key, "count": value} for key, value in counter.most_common(8)]


def product_insights(db: Session) -> list[dict]:
    products = {item.id: item for item in db.scalars(select(Product)).all()}
    recommendation_events = db.scalars(select(RecommendationEvent)).all()
    orders = db.scalars(select(Order).where(Order.order_status == "paid")).all()
    heat_counter: Counter[str] = Counter()
    paid_counter: Counter[str] = Counter()

    for event in recommendation_events:
        for product in event.recommended_products:
            heat_counter[product["product_id"]] += 1
    for order in orders:
        paid_counter[order.product_id] += 1

    items = []
    for product_id, heat in heat_counter.most_common():
        product = products.get(product_id)
        if not product:
            continue
        paid = paid_counter.get(product_id, 0)
        items.append(
            {
                "product_id": product_id,
                "product_name": product.name,
                "heat": heat,
                "paid_orders": paid,
                "low_conversion_risk": heat >= 5 and paid <= 1,
            }
        )
    return items[:10]


def team_weaknesses(db: Session) -> list[dict]:
    ranking = get_ranking(db)
    grouped: defaultdict[str, list[float]] = defaultdict(list)
    for item in ranking:
        for key, value in item["dimensions"].items():
            grouped[key].append(float(value))
    suggestions = {
        "reception": "接待开场还不稳定，建议补新人首问 SOP。",
        "recommendation": "推荐理由偏薄，建议补场景化推荐训练。",
        "conversion": "推进成交偏弱，建议重点练高价异议与收口。",
        "value": "客单提升空间大，建议增加礼盒与商务场景演练。",
    }
    scores = []
    for key, values in grouped.items():
        average = round(sum(values) / len(values), 2) if values else 0.0
        scores.append(
            {
                "dimension": key,
                "score": average,
                "suggestion": suggestions.get(key, "建议继续复盘。"),
            }
        )
    return sorted(scores, key=lambda item: item["score"])[:4]
