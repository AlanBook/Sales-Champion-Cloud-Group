from sqlalchemy import text

from sales_champion_backend.db.session import SessionLocal
from sales_champion_backend.services.seed_service import load_demo_seed


def main() -> None:
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
        load_demo_seed(db)
        db.commit()
