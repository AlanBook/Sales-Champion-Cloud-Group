from typing import Annotated

from fastapi import APIRouter, Depends

from sales_champion_backend.api.deps import get_current_user
from sales_champion_backend.db.models import User
from sales_champion_backend.schemas import DemoScenario

router = APIRouter()


@router.get("/scenarios", response_model=list[DemoScenario])
def scenarios(_: Annotated[User, Depends(get_current_user)]) -> list[DemoScenario]:
    return [
        DemoScenario(
            title="自饮推荐",
            customer_input="平时自己喝，口感清一点，预算500以内。",
            system_expectation=["识别 self_drink", "推荐 2-3 款", "生成简洁话术"],
        ),
        DemoScenario(
            title="送领导",
            customer_input="送领导，1500 左右预算，想体面一点。",
            system_expectation=["识别 gift_leader", "推荐礼盒", "给体面、安全、不出错的话术"],
        ),
        DemoScenario(
            title="高价异议",
            customer_input="为什么这款茶这么贵？",
            system_expectation=["输出价值解释逻辑", "避免空洞吹捧", "给风险提示"],
        ),
        DemoScenario(
            title="老板看板",
            customer_input="展示最近一周的老板洞察。",
            system_expectation=["看接待/成交/排行", "看高咨询低成交", "看高价异议薄弱导购"],
        ),
    ]
