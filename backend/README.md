## 销冠云团后端

FastAPI + SQLAlchemy + Alembic + PostgreSQL/pgvector 实现的高端茶 Demo 后端。

### 运行

```bash
uv sync
uv run alembic upgrade head
uv run seed-demo
uv run uvicorn sales_champion_backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 测试

```bash
uv run pytest
```
