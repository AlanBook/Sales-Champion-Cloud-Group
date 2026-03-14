from sales_champion_backend.core.security import create_access_token, decode_access_token
from sales_champion_backend.schemas import TrainingEvaluateRequest
from sales_champion_backend.services.assistant_service import (
    detect_budget,
    detect_scene,
    detect_tastes,
)
from sales_champion_backend.services.analytics_service import _top_staff_overview_items
from sales_champion_backend.services.champion_service import _dimension_score
from sales_champion_backend.services.training_service import evaluate_training


def test_detect_scene_for_gift_leader() -> None:
    scene, intent = detect_scene("送领导，1500 左右预算，想体面一点", None)
    assert scene == "gift_leader"
    assert intent == "gift"


def test_budget_and_taste_detection() -> None:
    assert detect_budget("平时自己喝，预算 500 以内", None) == "0-500"
    assert "清香" in detect_tastes("口感清一点，想顺口些", [])


def test_training_evaluation_returns_rewrite() -> None:
    result = evaluate_training(
        TrainingEvaluateRequest(
            staff_id="staff_01",
            scenario={"scene": "self_drink", "customer_message": "平时自己喝，预算 500 内"},
            sales_reply="您可以看看这款白茶。",
        )
    )
    assert result.score > 0
    assert result.rewritten_reply
    assert result.dimension_scores["clarity"] >= 60


def test_champion_dimension_score_uses_thresholds() -> None:
    score = _dimension_score(
        {
            "metrics": [
                {"metric_code": "reception_count", "threshold": 40, "weight": 0.5},
                {"metric_code": "conversion_rate", "threshold": 0.4, "weight": 0.5},
            ]
        },
        {
            "reception_count": 32,
            "conversion_rate": 0.36,
        },
    )
    assert score > 0
    assert score <= 100


def test_top_staff_overview_items_match_schema_shape() -> None:
    items = _top_staff_overview_items(
        [
            {
                "staff_id": "staff-1",
                "name": "导购甲",
                "total_score": 88.6,
                "dimensions": {"conversion": 80},
            }
        ]
    )
    assert items == [{"staff_id": "staff-1", "name": "导购甲", "score": 88.6}]


def test_token_round_trip() -> None:
    token = create_access_token("user-1", "boss")
    payload = decode_access_token(token)
    assert payload["sub"] == "user-1"
    assert payload["role_code"] == "boss"
