# 销冠云团（高端茶 Demo 版）

基于 `sales_champion_codex_pack` 约束实现的最小可运行版本，目标是把“老板驾驶舱 × 导购销冠助手 × 知识沉淀底座 × 新人陪练”完整落成一个可本地启动、可路演的 Web MVP。

## 目录

- `frontend/`：Next.js + TypeScript + Tailwind 前端
- `backend/`：FastAPI + SQLAlchemy + Alembic 后端
- `schemas/`：结构化输出 schema
- `prompts/`：保留的提示模板
- `docker-compose.yml`：本地拉起 PostgreSQL/pgvector、Redis、前后端

## 路由

- `/login`：登录页
- `/dashboard`：老板驾驶舱首页
- `/ranking`：导购排行 / 销冠指数
- `/questions`：高频问题与异议分析
- `/product-insights`：商品洞察页
- `/knowledge`：知识库管理页
- `/assistant`：导购销冠助手
- `/training`：新人陪练

## Demo 账号

- `boss_demo / password`
- `manager_demo / password`
- `admin_demo / password`
- `staff_08 / password`

## 本地启动

1. 复制环境变量模板：

```bash
cp .env.example .env
```

2. 用 Docker Compose 启动：

```bash
docker compose up --build
```

3. 打开：

- 前端：[http://localhost:3000](http://localhost:3000)
- 后端 OpenAPI：[http://localhost:8000/docs](http://localhost:8000/docs)

首次冷启动如果本机没有缓存基础镜像，`docker compose up --build` 会先拉 `node:20-alpine` 和 `python:3.12-slim`，耗时会明显更长。

## Windows 一键启动

项目已附带 Windows 启动器，目录在 `windows/`。

Windows 用户只需要：

1. 安装并启动 Docker Desktop for Windows
2. 解压项目压缩包
3. 双击 `start-sales-champion.bat`

启动器会自动：

- 检查 Docker Desktop
- 拉起容器
- 等待服务就绪
- 自动打开登录页

停止服务：

- 双击 `stop-sales-champion.bat`

重置演示数据：

- 双击 `reset-sales-champion-data.bat`

## 不用 Docker 的开发命令

### Backend

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run seed-demo
uv run uvicorn sales_champion_backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

## 已实现

- FastAPI 核心 API：鉴权、商品、知识库、导购助手、陪练、Dashboard、销冠规则、种子数据
- PostgreSQL/pgvector 模型与 Alembic 初始化迁移
- 10 个商品、20 FAQ、20 销冠案例、20 异议案例、8 名导购、100 条样例会话的种子数据
- 销冠指数计算、排行和个人详情
- 老板端多页面后台和导购助手/陪练/知识库前端
- evidence sources 输出
- Docker Compose 四服务联调通过

## 已验证

- `uv run pytest`
- `pnpm lint`
- `pnpm typecheck`
- `pnpm build`
- `docker compose up --build -d`
- `boss_demo / password` 登录
- `/dashboard`、`/assistant`、`/training`、`/knowledge` 页面和 API 闭环
- Windows 启动脚本和分发包生成脚本

## 说明

- 这版 AI 输出采用 `Demo provider` 风格的规则化生成，重点是先跑通结构化闭环、证据链和老板端回流。
- Redis 已在 Compose 中预留，但本版主要用于后续扩展，当前未引入复杂队列任务。
- 为保证容器和弱网环境稳定，前端已改为系统中文字体栈，不依赖 Google Fonts。
