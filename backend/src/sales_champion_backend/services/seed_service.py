from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from sales_champion_backend.core.config import get_settings
from sales_champion_backend.core.security import get_password_hash
from sales_champion_backend.db.models import (
    ChampionCase,
    ChampionScoreRule,
    ChampionScoreRuleItem,
    ConversationSession,
    Customer,
    FAQItem,
    ObjectionCase,
    ObjectionEvent,
    Order,
    Product,
    ProductScene,
    Role,
    SalesPlaybook,
    StaffDailyMetric,
    StaffProfile,
    Store,
    User,
)
from sales_champion_backend.schemas import AssistantRecommendRequest, KnowledgeIngestRequest
from sales_champion_backend.services.assistant_service import recommend
from sales_champion_backend.services.champion_service import (
    calculate_period_scores,
    latest_period_value,
)
from sales_champion_backend.services.retrieval_service import ingest_document


PRODUCT_SEEDS = [
    {
        "sku_code": "tea_001",
        "name": "岩骨花香·武夷岩茶礼盒",
        "category": "岩茶",
        "price": Decimal("1280"),
        "price_band": "500-1500",
        "origin": "福建武夷山",
        "craft": "中足火",
        "grade_level": "特级",
        "taste_profile": ["醇厚", "焙火"],
        "aroma_profile": ["花香", "岩韵"],
        "packaging_level": "商务礼盒",
        "gift_suitability": "高",
        "self_drink_suitability": "中",
        "business_gift_suitability": "高",
        "description": "适合送领导和商务礼赠的稳妥型武夷岩茶礼盒。",
        "selling_points": ["包装体面", "送礼不出错", "岩韵清晰"],
        "taboo_notes": ["若客户偏极轻口感，可换白茶"],
        "scenes": [
            {"scene_code": "gift_leader", "fit_score": 92, "reason": "礼盒体面、稳妥。"},
            {"scene_code": "business_visit", "fit_score": 89, "reason": "商务接待安全。"},
        ],
    },
    {
        "sku_code": "tea_002",
        "name": "山野清甜·高山白茶",
        "category": "白茶",
        "price": Decimal("468"),
        "price_band": "0-500",
        "origin": "福建福鼎",
        "craft": "日晒萎凋",
        "grade_level": "一级",
        "taste_profile": ["清香", "甘甜"],
        "aroma_profile": ["毫香"],
        "packaging_level": "简雅礼盒",
        "gift_suitability": "中",
        "self_drink_suitability": "高",
        "business_gift_suitability": "中",
        "description": "更适合日常自饮和新手客的清口白茶。",
        "selling_points": ["顺口清甜", "新手友好", "自饮负担小"],
        "taboo_notes": ["若客户追求强烈焙火香，不建议首推"],
        "scenes": [
            {"scene_code": "self_drink", "fit_score": 93, "reason": "顺口、容易接受。"},
            {"scene_code": "beginner_help", "fit_score": 90, "reason": "新手不容易踩坑。"},
        ],
    },
    {
        "sku_code": "tea_003",
        "name": "陈香醇润·熟普礼匣",
        "category": "普洱",
        "price": Decimal("1580"),
        "price_band": "1500-3000",
        "origin": "云南勐海",
        "craft": "熟茶渥堆",
        "grade_level": "收藏级",
        "taste_profile": ["醇厚", "陈香"],
        "aroma_profile": ["枣香", "陈香"],
        "packaging_level": "收藏礼匣",
        "gift_suitability": "高",
        "self_drink_suitability": "中",
        "business_gift_suitability": "高",
        "description": "适合送长辈与偏陈香口感客群的高段位熟普。",
        "selling_points": ["陈香稳定", "礼赠感强", "适合长辈"],
        "taboo_notes": ["年轻客若偏清香，不建议首推"],
        "scenes": [
            {"scene_code": "gift_elder", "fit_score": 94, "reason": "口感温和，适合长辈。"},
            {"scene_code": "business_visit", "fit_score": 83, "reason": "商务礼赠也够体面。"},
        ],
    },
    {
        "sku_code": "tea_004",
        "name": "正山雅韵·金骏眉",
        "category": "红茶",
        "price": Decimal("680"),
        "price_band": "500-1500",
        "origin": "福建桐木关",
        "craft": "红茶全发酵",
        "grade_level": "特级",
        "taste_profile": ["甘甜", "柔和"],
        "aroma_profile": ["蜜香"],
        "packaging_level": "雅致盒装",
        "gift_suitability": "高",
        "self_drink_suitability": "高",
        "business_gift_suitability": "中",
        "description": "兼顾礼赠与自饮，接受度高的安全款红茶。",
        "selling_points": ["接受度高", "礼赠体面", "香甜顺口"],
        "taboo_notes": ["客户若要更高收藏属性，可升级"],
        "scenes": [
            {"scene_code": "gift_leader", "fit_score": 85, "reason": "稳妥顺口。"},
            {"scene_code": "self_drink", "fit_score": 82, "reason": "柔和顺口，容易成交。"},
        ],
    },
    {
        "sku_code": "tea_005",
        "name": "清雅明前·龙井",
        "category": "绿茶",
        "price": Decimal("520"),
        "price_band": "500-1500",
        "origin": "浙江西湖",
        "craft": "明前炒青",
        "grade_level": "一级",
        "taste_profile": ["清香", "鲜爽"],
        "aroma_profile": ["豆香"],
        "packaging_level": "简约盒装",
        "gift_suitability": "中",
        "self_drink_suitability": "高",
        "business_gift_suitability": "中",
        "description": "适合清口偏好和日常自饮的高辨识度绿茶。",
        "selling_points": ["鲜爽清口", "认知度高", "春茶故事感强"],
        "taboo_notes": ["不适合长期存放送藏家"],
        "scenes": [
            {"scene_code": "self_drink", "fit_score": 88, "reason": "清爽易懂。"},
            {"scene_code": "beginner_help", "fit_score": 82, "reason": "认知度高，好解释。"},
        ],
    },
    {
        "sku_code": "tea_006",
        "name": "陈皮白茶·商务伴手礼",
        "category": "白茶",
        "price": Decimal("980"),
        "price_band": "500-1500",
        "origin": "福建福鼎",
        "craft": "拼配窖藏",
        "grade_level": "礼赠级",
        "taste_profile": ["甘甜", "清香"],
        "aroma_profile": ["陈皮香"],
        "packaging_level": "伴手礼包装",
        "gift_suitability": "高",
        "self_drink_suitability": "中",
        "business_gift_suitability": "高",
        "description": "更适合商务拜访和礼赠的陈皮白茶组合。",
        "selling_points": ["识别度高", "送礼故事好讲", "接受度高"],
        "taboo_notes": ["若客户排斥拼配概念需提前解释"],
        "scenes": [
            {"scene_code": "business_visit", "fit_score": 91, "reason": "商务礼赠轻松好讲。"},
            {"scene_code": "gift_leader", "fit_score": 80, "reason": "也可作为稳妥礼赠款。"},
        ],
    },
    {
        "sku_code": "tea_007",
        "name": "高焙火·牛栏坑肉桂",
        "category": "岩茶",
        "price": Decimal("2980"),
        "price_band": "1500-3000",
        "origin": "福建武夷山",
        "craft": "高焙火",
        "grade_level": "高端",
        "taste_profile": ["醇厚", "焙火"],
        "aroma_profile": ["辛香", "岩骨"],
        "packaging_level": "高端礼盒",
        "gift_suitability": "高",
        "self_drink_suitability": "中",
        "business_gift_suitability": "高",
        "description": "适合高价位礼赠和懂茶客户的代表性肉桂。",
        "selling_points": ["山场辨识度强", "高价位更有说服力", "适合做价值解释"],
        "taboo_notes": ["不适合完全不懂茶的新手客第一款"],
        "scenes": [
            {"scene_code": "gift_leader", "fit_score": 93, "reason": "高端体面且有话题。"},
            {"scene_code": "collect", "fit_score": 86, "reason": "懂茶客认可度高。"},
        ],
    },
    {
        "sku_code": "tea_008",
        "name": "岁月金砖·老白茶礼盒",
        "category": "白茶",
        "price": Decimal("1680"),
        "price_band": "1500-3000",
        "origin": "福建福鼎",
        "craft": "陈化",
        "grade_level": "礼赠级",
        "taste_profile": ["醇厚", "甘甜"],
        "aroma_profile": ["药香", "枣香"],
        "packaging_level": "典藏礼盒",
        "gift_suitability": "高",
        "self_drink_suitability": "中",
        "business_gift_suitability": "高",
        "description": "适合送长辈和重要商务对象的老白茶礼盒。",
        "selling_points": ["老茶故事强", "送礼安全稳妥", "口感温和"],
        "taboo_notes": ["若客户要非常清爽口感，可换绿茶或轻发酵茶"],
        "scenes": [
            {"scene_code": "gift_elder", "fit_score": 92, "reason": "更适合长辈接受。"},
            {"scene_code": "gift_leader", "fit_score": 84, "reason": "礼盒质感足。"},
        ],
    },
    {
        "sku_code": "tea_009",
        "name": "兰香单丛·品鉴装",
        "category": "乌龙",
        "price": Decimal("420"),
        "price_band": "0-500",
        "origin": "广东潮州",
        "craft": "轻焙火",
        "grade_level": "品鉴级",
        "taste_profile": ["花香", "清香"],
        "aroma_profile": ["兰花香"],
        "packaging_level": "轻礼盒",
        "gift_suitability": "中",
        "self_drink_suitability": "高",
        "business_gift_suitability": "低",
        "description": "适合喜欢花香调、自饮尝鲜的单丛入门品。",
        "selling_points": ["花香明显", "价格友好", "适合尝鲜"],
        "taboo_notes": ["不适合需要极强礼赠体面的客户"],
        "scenes": [
            {"scene_code": "self_drink", "fit_score": 84, "reason": "花香明显，适合自饮。"},
            {"scene_code": "beginner_help", "fit_score": 78, "reason": "口味鲜明好解释。"},
        ],
    },
    {
        "sku_code": "tea_010",
        "name": "商务金选·高端组合礼盒",
        "category": "礼盒",
        "price": Decimal("3680"),
        "price_band": "3000+",
        "origin": "组合装",
        "craft": "拼配组合",
        "grade_level": "旗舰",
        "taste_profile": ["醇厚", "清香"],
        "aroma_profile": ["复合香"],
        "packaging_level": "旗舰礼盒",
        "gift_suitability": "高",
        "self_drink_suitability": "低",
        "business_gift_suitability": "高",
        "description": "面向高预算商务礼赠的旗舰组合礼盒。",
        "selling_points": ["预算上探时更有排面", "多茶组合更安全", "适合企业送礼"],
        "taboo_notes": ["若客户只追求自饮性价比，不建议首推"],
        "scenes": [
            {"scene_code": "business_visit", "fit_score": 95, "reason": "高预算商务礼赠首选。"},
            {"scene_code": "gift_leader", "fit_score": 90, "reason": "预算充足时更体面。"},
        ],
    },
]

FAQ_SEEDS = [
    ("为什么这款茶这么贵？", "价格高通常来自原料等级、山场、工艺和礼赠场景价值。", "price_high"),
    ("我不懂茶怎么选？", "先按场景、预算和口味选，不要一上来就被专业名词压住。", "dont_understand_tea"),
    ("送领导怎么选更稳妥？", "优先礼盒体面、认知度高、解释不冒险的款。", "gift_unsure"),
    ("送长辈选什么更合适？", "优先温和顺口、认知门槛低、喝起来舒服的茶。", "gift_unsure"),
    ("和别家有什么不同？", "重点讲山场、工艺、稳定度和服务体验。", "compare_other_brand"),
] * 4

OBJECTION_TYPES = [
    "price_high",
    "dont_understand_tea",
    "gift_unsure",
    "compare_other_brand",
    "worth_it",
]


def _ensure_roles(db: Session) -> None:
    if db.scalar(select(Role).where(Role.code == "admin")):
        return
    db.add_all(
        [
            Role(code="admin", name="系统管理员", description="系统维护"),
            Role(code="boss", name="老板", description="经营负责人"),
            Role(code="manager", name="店长", description="门店负责人"),
            Role(code="staff", name="导购", description="销售顾问"),
        ]
    )


def _create_users(db: Session, store_id: str) -> list[User]:
    if db.scalar(select(User).where(User.username == "boss_demo")):
        return db.scalars(select(User)).all()
    password_hash = get_password_hash(get_settings().demo_seed_password)
    base_users = [
        ("admin_demo", "系统管理员", "admin"),
        ("boss_demo", "老板A", "boss"),
        ("manager_demo", "店长A", "manager"),
    ]
    staff_names = [
        ("staff_01", "导购林岚", "新人"),
        ("staff_02", "导购周禾", "新人"),
        ("staff_03", "导购陈岩", "普通"),
        ("staff_04", "导购宋枝", "普通"),
        ("staff_05", "导购唐煦", "普通"),
        ("staff_06", "导购叶青", "骨干"),
        ("staff_07", "导购顾川", "骨干"),
        ("staff_08", "导购许白", "销冠"),
    ]
    users: list[User] = []
    for username, display_name, role_code in base_users:
        user = User(
            username=username,
            display_name=display_name,
            email=f"{username}@demo.local",
            password_hash=password_hash,
            role_code=role_code,
            store_id=store_id,
            is_active=True,
        )
        db.add(user)
        users.append(user)
    for index, (username, display_name, level) in enumerate(staff_names):
        user = User(
            username=username,
            display_name=display_name,
            email=f"{username}@demo.local",
            password_hash=password_hash,
            role_code="staff",
            store_id=store_id,
            is_active=True,
        )
        db.add(user)
        db.flush()
        db.add(
            StaffProfile(
                user_id=user.id,
                hire_date=date.today() - timedelta(days=240 - index * 20),
                level=level,
                specialty_tags=["送礼", "价值解释"] if level in {"骨干", "销冠"} else ["自饮"],
                notes="高端茶 Demo 演示导购",
            )
        )
        users.append(user)
    db.flush()
    return users


def _create_products(db: Session) -> list[Product]:
    if db.scalar(select(Product).where(Product.sku_code == "tea_001")):
        return db.scalars(select(Product)).all()
    products: list[Product] = []
    for seed in PRODUCT_SEEDS:
        payload = dict(seed)
        scenes = payload.pop("scenes")
        product = Product(**payload)
        db.add(product)
        db.flush()
        for scene in scenes:
            db.add(ProductScene(product_id=product.id, **scene))
        products.append(product)
    db.flush()
    return products


def _seed_knowledge(db: Session, products: list[Product]) -> None:
    if db.scalar(select(FAQItem)):
        return
    product_map = {index % len(products): product for index, product in enumerate(products)}
    for index, (question, answer, category) in enumerate(FAQ_SEEDS):
        product = product_map[index % len(product_map)]
        document = ingest_document(
            db,
            KnowledgeIngestRequest(
                doc_type="faq",
                title=f"FAQ {index + 1}：{question}",
                content=f"{question}\n{answer}\n适用商品：{product.name}",
                metadata={"category": category, "scene_code": "gift_leader" if "送领导" in question else "self_drink"},
                source_type="seed",
                source_ref=f"faq_{index + 1:03d}",
            ),
        )
        db.add(
            FAQItem(
                question=question,
                answer=answer,
                category=category,
                related_product_id=product.id,
                scene_code="gift_leader" if "送领导" in question else "self_drink",
                document_id=document.id,
            )
        )

    for index in range(20):
        objection_type = OBJECTION_TYPES[index % len(OBJECTION_TYPES)]
        document = ingest_document(
            db,
            KnowledgeIngestRequest(
                doc_type="objection_case",
                title=f"异议案例 {index + 1}",
                content=f"客户原话：为什么这款茶这么贵？\n处理逻辑：先解释{objection_type}，再回到场景价值。",
                metadata={"objection_type": objection_type},
                source_type="seed",
                source_ref=f"objection_{index + 1:03d}",
            ),
        )
        db.add(
            ObjectionCase(
                objection_type=objection_type,
                customer_quote="为什么这款茶这么贵？" if objection_type == "price_high" else "我不太懂茶怎么选。",
                handling_logic=["先确认场景", "解释价值", "给稳妥推荐"],
                suggested_pitch="它贵的不只是价格，更是原料、工艺和场景下的稳妥度。",
                risk_notes=["避免夸大保值属性", "避免先堆专业术语"],
                document_id=document.id,
            )
        )

    for index in range(20):
        scene_code = ["self_drink", "gift_leader", "gift_elder", "business_visit"][index % 4]
        document = ingest_document(
            db,
            KnowledgeIngestRequest(
                doc_type="champion_case",
                title=f"销冠案例 {index + 1}",
                content=f"场景：{scene_code}\n打法：先问用途，再给两档推荐，最后补高价解释。",
                metadata={"scene_code": scene_code},
                source_type="seed",
                source_ref=f"champion_{index + 1:03d}",
            ),
        )
        db.add(
            ChampionCase(
                title=f"{scene_code} 成交案例 {index + 1}",
                scene_code=scene_code,
                customer_profile={"budget": "500-1500", "intent": scene_code},
                highlights=["先问用途", "理由简单好懂", "最后收口"],
                transcript="客户先说需求，销冠再拆预算、口感、用途，最后成交。",
                key_patterns=["先追问", "再给两档推荐", "最后讲价值"],
                document_id=document.id,
            )
        )

    for scene_code in ["self_drink", "gift_leader", "gift_elder", "business_visit", "beginner_help"]:
        db.add(
            SalesPlaybook(
                title=f"{scene_code} 话术模板",
                scene_code=scene_code,
                objection_type="price_high" if scene_code != "beginner_help" else "dont_understand_tea",
                template_text="先问场景，再给推荐理由，再补价值解释。",
                metadata_json={"tone": "稳妥"},
            )
        )
    db.flush()


def _seed_rule(db: Session) -> ChampionScoreRule:
    rule = db.scalar(select(ChampionScoreRule).where(ChampionScoreRule.status == "active"))
    if rule:
        return rule
    rule = ChampionScoreRule(
        rule_name="高端茶销冠指数",
        version="v1",
        total_formula="接待能力*0.2 + 推荐能力*0.25 + 转化能力*0.35 + 成交价值*0.2",
        status="active",
        effective_from=date.today() - timedelta(days=30),
        effective_to=None,
    )
    db.add(rule)
    db.flush()
    items = [
        ("reception", "接待能力", Decimal("0.2000"), [{"metric_code": "reception_count", "threshold": 45, "weight": 1.0}]),
        (
            "recommendation",
            "推荐能力",
            Decimal("0.2500"),
            [
                {"metric_code": "recommendation_rate", "threshold": 0.85, "weight": 0.6},
                {"metric_code": "objection_resolution_rate", "threshold": 0.75, "weight": 0.4},
            ],
        ),
        (
            "conversion",
            "转化能力",
            Decimal("0.3500"),
            [
                {"metric_code": "conversion_rate", "threshold": 0.35, "weight": 0.7},
                {"metric_code": "conversion_count", "threshold": 12, "weight": 0.3},
            ],
        ),
        (
            "value",
            "成交价值",
            Decimal("0.2000"),
            [
                {"metric_code": "avg_order_value", "threshold": 1800, "weight": 0.7},
                {"metric_code": "high_price_handled", "threshold": 8, "weight": 0.3},
            ],
        ),
    ]
    for dimension_code, dimension_name, weight, metrics in items:
        db.add(
            ChampionScoreRuleItem(
                rule_id=rule.id,
                dimension_code=dimension_code,
                dimension_name=dimension_name,
                weight=weight,
                config_json={"metrics": metrics},
            )
        )
    db.flush()
    return rule


def _seed_sessions_and_metrics(db: Session, staff_users: list[User], products: list[Product]) -> None:
    if db.scalar(select(ConversationSession)):
        return
    scenario_messages = [
        ("平时自己喝，口感清一点，预算500以内。", "self_drink"),
        ("送领导，1500左右预算，想体面一点。", "gift_leader"),
        ("送长辈，想稳妥一些。", "gift_elder"),
        ("商务拜访，预算高一点。", "business_visit"),
        ("我不懂茶，想买一款不容易出错的。", "beginner_help"),
        ("为什么这款茶卖这么贵？", "self_drink"),
    ]
    session_records: list[ConversationSession] = []
    for index in range(100):
        staff = staff_users[index % len(staff_users)]
        message, scene = scenario_messages[index % len(scenario_messages)]
        customer = Customer(
            source_channel="in_store",
            customer_segment="礼赠客" if "送" in message else "新客",
            preference_tags=["清香"] if scene == "self_drink" else ["醇厚"],
            notes=message,
        )
        db.add(customer)
        db.flush()
        result = recommend(
            db,
            AssistantRecommendRequest(
                staff_id=staff.id,
                customer_id=customer.id,
                session_id=None,
                input={
                    "customer_message": message,
                    "scene_hint": scene,
                    "budget_range": None,
                    "taste_preference": ["清香"] if scene == "self_drink" else ["醇厚"],
                },
            ),
        )
        session = db.get(ConversationSession, result.session_id)
        if not session:
            continue
        session.created_at = datetime.now(timezone.utc) - timedelta(days=index % 14, hours=index % 8)
        session.updated_at = session.created_at
        if index % 3 != 0:
            session.status = "completed"
            session.conversion_result = "converted"
            product = products[index % len(products)]
            db.add(
                Order(
                    session_id=session.id,
                    staff_id=staff.id,
                    product_id=product.id,
                    amount=product.price,
                    quantity=1,
                    order_status="paid",
                    created_at=session.created_at + timedelta(hours=1),
                )
            )
        else:
            session.status = "lost"
            session.conversion_result = "lost"
        session_records.append(session)

    metrics_map: dict[tuple[str, date], dict[str, Decimal | int]] = {}
    sessions = db.scalars(select(ConversationSession)).all()
    orders = db.scalars(select(Order).where(Order.order_status == "paid")).all()
    objections = db.scalars(select(ObjectionEvent)).all()

    for session in sessions:
        key = (session.staff_id, session.created_at.date())
        bucket = metrics_map.setdefault(
            key,
            {
                "reception_count": 0,
                "recommendation_count": 0,
                "conversion_count": 0,
                "revenue": Decimal("0"),
                "objection_resolved_count": 0,
                "high_price_objection_count": 0,
            },
        )
        bucket["reception_count"] += 1
        bucket["recommendation_count"] += 1
        if session.conversion_result == "converted":
            bucket["conversion_count"] += 1
    for order in orders:
        key = (order.staff_id, order.created_at.date())
        bucket = metrics_map.setdefault(
            key,
            {
                "reception_count": 0,
                "recommendation_count": 0,
                "conversion_count": 0,
                "revenue": Decimal("0"),
                "objection_resolved_count": 0,
                "high_price_objection_count": 0,
            },
        )
        bucket["revenue"] += order.amount
    for objection in objections:
        session = next((item for item in sessions if item.id == objection.session_id), None)
        if not session:
            continue
        key = (session.staff_id, objection.created_at.date())
        bucket = metrics_map.setdefault(
            key,
            {
                "reception_count": 0,
                "recommendation_count": 0,
                "conversion_count": 0,
                "revenue": Decimal("0"),
                "objection_resolved_count": 0,
                "high_price_objection_count": 0,
            },
        )
        bucket["high_price_objection_count"] += 1
        if objection.resolution_status == "handled":
            bucket["objection_resolved_count"] += 1

    for (staff_id, metric_date), values in metrics_map.items():
        avg_order_value = (
            Decimal(values["revenue"]) / values["conversion_count"]
            if values["conversion_count"]
            else Decimal("0")
        )
        conversion_rate = (
            Decimal(values["conversion_count"]) / Decimal(values["reception_count"])
            if values["reception_count"]
            else Decimal("0")
        )
        db.add(
            StaffDailyMetric(
                staff_id=staff_id,
                metric_date=metric_date,
                reception_count=int(values["reception_count"]),
                recommendation_count=int(values["recommendation_count"]),
                conversion_count=int(values["conversion_count"]),
                conversion_rate=round(conversion_rate, 2),
                avg_order_value=round(avg_order_value, 2),
                objection_resolved_count=int(values["objection_resolved_count"]),
                high_price_objection_count=int(values["high_price_objection_count"]),
                notes="seed generated",
            )
        )
    db.flush()


def _seed_snapshots(db: Session, rule: ChampionScoreRule) -> None:
    calculate_period_scores(
        db,
        rule_id=rule.id,
        period_type="week",
        period_value=latest_period_value(),
    )
    db.flush()


def load_demo_seed(db: Session) -> None:
    _ensure_roles(db)
    store = db.scalar(select(Store).where(Store.name == "高端茶旗舰店"))
    if not store:
        store = Store(name="高端茶旗舰店", city="杭州", region="华东")
        db.add(store)
        db.flush()
    users = _create_users(db, store.id)
    products = _create_products(db)
    _seed_knowledge(db, products)
    rule = _seed_rule(db)
    staff_users = [user for user in users if user.role_code == "staff"]
    _seed_sessions_and_metrics(db, staff_users, products)
    _seed_snapshots(db, rule)
