from __future__ import annotations

from sales_champion_backend.schemas import TrainingEvaluateRequest, TrainingEvaluateResponse


def evaluate_training(payload: TrainingEvaluateRequest) -> TrainingEvaluateResponse:
    reply = payload.sales_reply
    questioning = 55
    recommendation_fit = 60
    clarity = 62
    objection_readiness = 58
    missing_questions: list[str] = []
    suggestions: list[str] = []

    if "？" in reply or "?" in reply:
        questioning += 18
    else:
        missing_questions.append("是否先确认用途、预算和口味偏好")
        suggestions.append("先追问场景，再给推荐。")
    if any(keyword in reply for keyword in ["预算", "口感", "自饮", "送礼", "领导"]):
        recommendation_fit += 16
    else:
        missing_questions.append("是否确认是自饮、送礼还是商务礼赠")
    if len(reply) >= 36:
        clarity += 14
    if any(keyword in reply for keyword in ["原料", "工艺", "山场", "稳妥", "不容易出错"]):
        objection_readiness += 18
    else:
        suggestions.append("补一段价值解释，避免只报商品名。")

    score = round((questioning + recommendation_fit + clarity + objection_readiness) / 4)
    rewritten_reply = (
        "我先帮您把需求问完整：这次主要是自己喝还是也考虑送人？"
        "如果是自己喝、预算控制在这个范围内，我建议先看两款口感更稳妥的茶，"
        "再根据您更偏清香还是更醇一些做最后收口。"
    )
    return TrainingEvaluateResponse(
        score=score,
        dimension_scores={
            "questioning": questioning,
            "recommendation_fit": recommendation_fit,
            "clarity": clarity,
            "objection_readiness": objection_readiness,
        },
        missing_questions=missing_questions or ["已覆盖基础追问，可继续细化送礼对象。"],
        improvement_suggestions=suggestions or ["表达顺序基本正确，可继续压缩成更好讲的成交话术。"],
        rewritten_reply=rewritten_reply,
    )
