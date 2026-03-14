from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from statistics import mean
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from sales_champion_backend.db.models import (
    ChampionScoreRule,
    ChampionScoreRuleItem,
    ChampionScoreSnapshot,
    StaffDailyMetric,
    StaffProfile,
    User,
)


def _date_range_for_period(period_type: str, period_value: str) -> tuple[date, date]:
    if period_type == "day":
        day = date.fromisoformat(period_value)
        return day, day
    if period_type == "week":
        year, week = period_value.split("-W")
        start = date.fromisocalendar(int(year), int(week), 1)
        return start, start + timedelta(days=6)
    if period_type == "month":
        year, month = period_value.split("-")
        start = date(int(year), int(month), 1)
        if int(month) == 12:
            next_month = date(int(year) + 1, 1, 1)
        else:
            next_month = date(int(year), int(month) + 1, 1)
        return start, next_month - timedelta(days=1)
    raise ValueError("不支持的周期类型。")


def get_active_rule(db: Session) -> ChampionScoreRule | None:
    return db.scalar(
        select(ChampionScoreRule)
        .where(ChampionScoreRule.status == "active")
        .order_by(ChampionScoreRule.effective_from.desc())
    )


def _normalize(value: float, threshold: float) -> float:
    if threshold <= 0:
        return 0
    return round(min(value / threshold, 1.0) * 100, 2)


def _metric_value(metric_code: str, aggregate: dict[str, float]) -> float:
    reception_count = aggregate.get("reception_count", 0)
    conversion_count = aggregate.get("conversion_count", 0)
    recommendation_count = aggregate.get("recommendation_count", 0)
    avg_order_value = aggregate.get("avg_order_value", 0)
    objection_resolved_count = aggregate.get("objection_resolved_count", 0)
    high_price_objection_count = aggregate.get("high_price_objection_count", 0)
    conversion_rate = aggregate.get("conversion_rate", 0)

    if metric_code == "reception_count":
        return reception_count
    if metric_code == "recommendation_rate":
        return recommendation_count / reception_count if reception_count else 0
    if metric_code == "conversion_rate":
        return conversion_rate
    if metric_code == "objection_resolution_rate":
        return (
            objection_resolved_count / high_price_objection_count
            if high_price_objection_count
            else 0.5
        )
    if metric_code == "avg_order_value":
        return avg_order_value
    if metric_code == "conversion_count":
        return conversion_count
    if metric_code == "high_price_handled":
        return objection_resolved_count
    return 0


def _dimension_score(config_json: dict[str, Any], aggregate: dict[str, float]) -> float:
    metrics = config_json.get("metrics", [])
    if not metrics:
        return 0
    weighted_scores: list[float] = []
    total_weight = 0.0
    for metric in metrics:
        threshold = float(metric.get("threshold", 1))
        value = _metric_value(metric["metric_code"], aggregate)
        normalized = _normalize(value, threshold)
        weight = float(metric.get("weight", 1))
        total_weight += weight
        weighted_scores.append(normalized * weight)
    if total_weight == 0:
        return 0
    return round(sum(weighted_scores) / total_weight, 2)


def calculate_period_scores(
    db: Session,
    *,
    rule_id: str,
    period_type: str,
    period_value: str,
) -> list[ChampionScoreSnapshot]:
    start_date, end_date = _date_range_for_period(period_type, period_value)
    rule = db.get(ChampionScoreRule, rule_id)
    if not rule:
        raise ValueError("规则不存在。")
    items = db.scalars(
        select(ChampionScoreRuleItem).where(ChampionScoreRuleItem.rule_id == rule_id)
    ).all()
    metrics = db.scalars(
        select(StaffDailyMetric).where(
            StaffDailyMetric.metric_date >= start_date,
            StaffDailyMetric.metric_date <= end_date,
        )
    ).all()
    grouped: dict[str, list[StaffDailyMetric]] = {}
    for metric in metrics:
        grouped.setdefault(metric.staff_id, []).append(metric)

    db.execute(
        delete(ChampionScoreSnapshot).where(
            ChampionScoreSnapshot.rule_id == rule_id,
            ChampionScoreSnapshot.period_type == period_type,
            ChampionScoreSnapshot.period_value == period_value,
        )
    )

    snapshots: list[ChampionScoreSnapshot] = []
    for staff_id, values in grouped.items():
        aggregate = {
            "reception_count": sum(item.reception_count for item in values),
            "recommendation_count": sum(item.recommendation_count for item in values),
            "conversion_count": sum(item.conversion_count for item in values),
            "conversion_rate": float(mean(float(item.conversion_rate) for item in values)),
            "avg_order_value": float(mean(float(item.avg_order_value) for item in values)),
            "objection_resolved_count": sum(item.objection_resolved_count for item in values),
            "high_price_objection_count": sum(item.high_price_objection_count for item in values),
        }
        dimension_scores: dict[str, float] = {}
        diagnostics: list[str] = []
        total_score = 0.0
        for item in items:
            score = _dimension_score(item.config_json, aggregate)
            dimension_scores[item.dimension_code] = score
            total_score += score * float(item.weight)
            if score < 70:
                diagnostics.append(f"{item.dimension_name}偏弱，建议补训练与复盘。")

        snapshot = ChampionScoreSnapshot(
            rule_id=rule_id,
            staff_id=staff_id,
            period_type=period_type,
            period_value=period_value,
            total_score=round(total_score, 2),
            dimension_scores=dimension_scores,
            diagnostic_notes=diagnostics or ["表现稳定，可继续复制销冠打法。"],
        )
        db.add(snapshot)
        snapshots.append(snapshot)
    db.flush()
    return snapshots


def latest_period_value() -> str:
    today = date.today()
    iso_year, iso_week, _ = today.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def get_ranking(db: Session) -> list[dict[str, Any]]:
    rule = get_active_rule(db)
    if not rule:
        return []
    period_value = latest_period_value()
    snapshots = db.scalars(
        select(ChampionScoreSnapshot).where(
            ChampionScoreSnapshot.rule_id == rule.id,
            ChampionScoreSnapshot.period_type == "week",
            ChampionScoreSnapshot.period_value == period_value,
        )
    ).all()
    if not snapshots:
        snapshots = calculate_period_scores(
            db,
            rule_id=rule.id,
            period_type="week",
            period_value=period_value,
        )
        db.flush()
    users = {
        user.id: user
        for user in db.scalars(select(User).where(User.role_code == "staff")).all()
    }
    profiles = {
        profile.user_id: profile
        for profile in db.scalars(select(StaffProfile)).all()
    }
    ranking = []
    for snapshot in snapshots:
        user = users.get(snapshot.staff_id)
        profile = profiles.get(snapshot.staff_id)
        if not user:
            continue
        ranking.append(
            {
                "staff_id": user.id,
                "name": user.display_name,
                "level": profile.level if profile else "staff",
                "total_score": float(snapshot.total_score),
                "dimensions": {
                    key: float(value) for key, value in snapshot.dimension_scores.items()
                },
            }
        )
    return sorted(ranking, key=lambda item: item["total_score"], reverse=True)


def get_staff_detail(db: Session, staff_id: str) -> dict[str, Any]:
    ranking = get_ranking(db)
    target = next((item for item in ranking if item["staff_id"] == staff_id), None)
    if not target:
        raise ValueError("未找到该导购的销冠快照。")
    snapshot = db.scalar(
        select(ChampionScoreSnapshot)
        .where(ChampionScoreSnapshot.staff_id == staff_id)
        .order_by(ChampionScoreSnapshot.created_at.desc())
    )
    diagnostics = snapshot.diagnostic_notes if snapshot else []
    radar = [
        {"dimension": key, "score": value}
        for key, value in target["dimensions"].items()
    ]
    return {
        "staff_id": target["staff_id"],
        "name": target["name"],
        "role_level": target["level"],
        "total_score": target["total_score"],
        "dimensions": target["dimensions"],
        "radar": radar,
        "diagnostics": diagnostics,
    }
