from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from sales_champion_backend.api.deps import DBSession, get_current_user, require_roles
from sales_champion_backend.db.models import Product, ProductScene, User
from sales_champion_backend.schemas import ProductCreate, ProductRead, ProductUpdate

router = APIRouter()


def _to_product_read(db: DBSession, product: Product) -> ProductRead:
    scenes = db.scalars(select(ProductScene).where(ProductScene.product_id == product.id)).all()
    return ProductRead(
        **product.__dict__,
        scenes=[
            {
                "scene_code": scene.scene_code,
                "fit_score": float(scene.fit_score),
                "reason": scene.reason,
            }
            for scene in scenes
        ],
    )


@router.get("", response_model=list[ProductRead])
def list_products(
    db: DBSession,
    _: Annotated[User, Depends(get_current_user)],
    category: str | None = None,
    price_band: str | None = None,
    keyword: str | None = None,
) -> list[ProductRead]:
    statement = select(Product).where(Product.is_active.is_(True))
    if category:
        statement = statement.where(Product.category == category)
    if price_band:
        statement = statement.where(Product.price_band == price_band)
    if keyword:
        statement = statement.where(Product.name.contains(keyword))
    products = db.scalars(statement.order_by(Product.price.desc())).all()
    return [_to_product_read(db, product) for product in products]


@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    product_id: str,
    db: DBSession,
    _: Annotated[User, Depends(get_current_user)],
) -> ProductRead:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在。")
    return _to_product_read(db, product)


@router.post("", response_model=ProductRead)
def create_product(
    payload: ProductCreate,
    db: DBSession,
    _: Annotated[User, Depends(require_roles("admin", "manager"))],
) -> ProductRead:
    scenes = payload.scenes
    product = Product(**payload.model_dump(exclude={"scenes"}))
    db.add(product)
    db.flush()
    for scene in scenes:
        db.add(ProductScene(product_id=product.id, **scene))
    db.flush()
    return _to_product_read(db, product)


@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: str,
    payload: ProductUpdate,
    db: DBSession,
    _: Annotated[User, Depends(require_roles("admin", "manager"))],
) -> ProductRead:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在。")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(product, key, value)
    db.flush()
    return _to_product_read(db, product)
