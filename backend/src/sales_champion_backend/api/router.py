from fastapi import APIRouter

from sales_champion_backend.api.routes import (
    assistant,
    auth,
    champion,
    dashboard,
    demo,
    knowledge,
    products,
    seed,
    training,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["assistant"])
api_router.include_router(training.router, prefix="/training", tags=["training"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(champion.router, prefix="/champion", tags=["champion"])
api_router.include_router(seed.router, prefix="/seed", tags=["seed"])
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
