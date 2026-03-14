from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from sales_champion_backend.api.deps import DBSession, get_current_user, require_roles
from sales_champion_backend.db.models import ChampionScoreRule, ChampionScoreRuleItem, User
from sales_champion_backend.schemas import ChampionCalculationRequest, ChampionRulePayload
from sales_champion_backend.services.champion_service import calculate_period_scores

router = APIRouter()


@router.get("/rules")
def list_rules(
    db: DBSession,
    _: Annotated[User, Depends(get_current_user)],
) -> list[dict]:
    rules = db.scalars(select(ChampionScoreRule)).all()
    items = db.scalars(select(ChampionScoreRuleItem)).all()
    item_map: dict[str, list[ChampionScoreRuleItem]] = {}
    for item in items:
        item_map.setdefault(item.rule_id, []).append(item)
    return [
        {
            "id": rule.id,
            "rule_name": rule.rule_name,
            "version": rule.version,
            "total_formula": rule.total_formula,
            "status": rule.status,
            "effective_from": rule.effective_from.isoformat(),
            "effective_to": rule.effective_to.isoformat() if rule.effective_to else None,
            "items": [
                {
                    "dimension_code": item.dimension_code,
                    "dimension_name": item.dimension_name,
                    "weight": float(item.weight),
                    "config_json": item.config_json,
                }
                for item in item_map.get(rule.id, [])
            ],
        }
        for rule in rules
    ]


@router.post("/rules")
def create_rule(
    payload: ChampionRulePayload,
    db: DBSession,
    _: Annotated[User, Depends(require_roles("admin", "boss"))],
) -> dict:
    rule = ChampionScoreRule(
        rule_name=payload.rule_name,
        version=payload.version,
        total_formula=payload.total_formula,
        status=payload.status,
        effective_from=payload.effective_from,
        effective_to=payload.effective_to,
    )
    db.add(rule)
    db.flush()
    for item in payload.items:
        db.add(
            ChampionScoreRuleItem(
                rule_id=rule.id,
                dimension_code=item.dimension_code,
                dimension_name=item.dimension_name,
                weight=item.weight,
                config_json=item.config_json,
            )
        )
    db.flush()
    return {"id": rule.id}


@router.put("/rules/{rule_id}")
def update_rule(
    rule_id: str,
    payload: ChampionRulePayload,
    db: DBSession,
    _: Annotated[User, Depends(require_roles("admin", "boss"))],
) -> dict:
    rule = db.get(ChampionScoreRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在。")
    rule.rule_name = payload.rule_name
    rule.version = payload.version
    rule.total_formula = payload.total_formula
    rule.status = payload.status
    rule.effective_from = payload.effective_from
    rule.effective_to = payload.effective_to
    db.flush()
    return {"ok": True}


@router.post("/calculate")
def calculate(
    payload: ChampionCalculationRequest,
    db: DBSession,
    _: Annotated[User, Depends(require_roles("admin", "boss", "manager"))],
) -> dict:
    snapshots = calculate_period_scores(
        db,
        rule_id=payload.rule_id,
        period_type=payload.period_type,
        period_value=payload.period_value,
    )
    return {"count": len(snapshots)}
