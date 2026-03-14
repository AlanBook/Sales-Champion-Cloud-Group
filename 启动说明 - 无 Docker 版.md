# 销冠云团 - 无 Docker 启动指南

## ✅ 快速启动（无需 Docker）

### 第一步：启动后端

```bash
cd "d:\code\销冠云团\windows\windows\sales-champion-demo-win\backend"
python run_server.py
```

或者双击运行：
```
backend\run_server.py
```

后端将运行在：http://localhost:8000

### 第二步：启动前端

打开新的终端窗口：

```bash
cd "d:\code\销冠云团\windows\windows\sales-champion-demo-win\frontend"
npm run dev
```

前端将运行在：http://localhost:3000

### 第三步：访问系统

在浏览器中打开 http://localhost:3000 或 http://localhost:3000/login

## 🔐 内置登录账号

- 👔 **老板账号**：`boss_demo` / `password`
- 📊 **经理账号**：`manager_demo` / `password`
- ⚙️ **管理员**：`admin_demo` / `password`
- 👤 **员工账号**：`staff_08` / `password`

## 🗄️ 数据库初始化

**重要提示**：首次运行时，需要先初始化数据库！

```bash
cd "d:\code\销冠云团\windows\windows\sales-champion-demo-win\backend"
python init_db.py
```

或者双击运行：
```
backend\init_db.py
```

这会：
1. 创建所有数据库表（SQLite）
2. 插入演示数据
3. 创建内置账号

## 📝 技术说明

### 已做的修改（无需 Docker）

1. ✅ **数据库**：使用 SQLite 替代 PostgreSQL
   - 数据库文件：`backend/sales_champion.db`
   - 无需安装数据库服务器

2. ✅ **向量搜索**：临时禁用 pgvector
   - 使用 JSON 字段存储向量数据
   - 功能完整，但搜索性能略低

3. ✅ **配置调整**：
   - 默认数据库改为 SQLite
   - CORS 支持前后端通信

### 项目结构

```
sales-champion-demo-win/
├── backend/
│   ├── run_server.py          # 后端启动脚本
│   ├── init_db.py             # 数据库初始化脚本
│   ├── .env                   # 环境配置
│   ├── sales_champion.db      # SQLite 数据库（自动生成）
│   └── src/
│       └── sales_champion_backend/
├── frontend/
│   ├── .env.local             # 前端配置
│   └── src/
└── README-Windows.md
```

## 🚀 常用命令

### 后端
```bash
# 初始化数据库
python init_db.py

# 启动后端服务
python run_server.py

# 查看 API 文档
http://localhost:8000/docs
```

### 前端
```bash
# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

## 🔧 故障排查

### 问题：登录时提示 "Failed to fetch"
**原因**：后端未启动或数据库未初始化

**解决**：
1. 确保后端已启动：http://localhost:8000/healthz 应返回 `{"status":"ok"}`
2. 运行数据库初始化：`python init_db.py`

### 问题：前端页面空白
**原因**：Node.js 版本或依赖问题

**解决**：
1. 检查 Node.js 版本：`node --version`（需要 v18+）
2. 重新安装依赖：`npm install`

### 问题：端口被占用
**解决**：
- 后端占用 8000 端口
- 前端占用 3000 端口
- 关闭占用程序或修改配置

### 重置数据库

如需清除所有数据重新开始：

```bash
# 删除数据库文件
del backend\sales_champion.db

# 重新初始化
python backend\init_db.py
```

## 📚 功能模块

### 老板驾驶舱
- 经营总览
- 销冠指数排行
- 商品热度分析
- 团队能力诊断

### 导购销冠助手
- 客户需求识别
- 场景化推荐
- 话术生成
- 异议处理

### 知识沉淀
- 销冠话术库
- FAQ 知识库
- 培训材料

## 🎯 下一步

1. 登录系统体验功能
2. 查看 API 文档：http://localhost:8000/docs
3. 修改配置满足自定义需求

---

**技术支持**：查看 `README.md` 获取更多信息
