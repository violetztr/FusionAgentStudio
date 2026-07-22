# Knowledge Fusion Agent Studio（知识融合智能体工作室）

多知识源 AI 智能体构建平台。支持将文档、网页、笔记等知识来源摄入知识库，将知识库绑定到可配置的智能体，并通过带引用和运行时追踪的调试聊天进行验证。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Next.js、React、TypeScript |
| 后端 | FastAPI、Python、SQLAlchemy、Alembic |
| 数据库 | PostgreSQL + pgvector（向量存储） |
| 任务队列 | Redis + Celery（异步摄入任务） |
| 模型层 | OpenAI 兼容的 Chat / Embedding API 网关 |

## 项目结构

```
FusionAgentStudio/
├── apps/
│   ├── api/                    # FastAPI 后端
│   │   ├── app/
│   │   │   ├── core/           # 配置管理
│   │   │   ├── db/             # 数据库模型与会话
│   │   │   ├── routes/         # API 路由（健康检查、知识库、来源、智能体、聊天、运行时日志）
│   │   │   ├── schemas/        # Pydantic 数据模型
│   │   │   ├── services/       # 业务逻辑层
│   │   │   │   ├── agent/      # 智能体管理
│   │   │   │   ├── agent_runtime/ # 智能体运行时（聊天、引用、提示构建）
│   │   │   │   ├── ingestion/  # 知识摄入（解析、清洗、分块、索引）
│   │   │   │   ├── knowledge/  # 知识库与来源管理
│   │   │   │   ├── logs/       # 运行时日志
│   │   │   │   ├── model_gateway/ # 模型网关（OpenAI 兼容）
│   │   │   │   └── retrieval/  # 混合检索（向量 + 关键词）
│   │   │   └── workers/        # Celery 异步任务
│   │   ├── alembic/            # 数据库迁移
│   │   └── tests/              # 后端单元测试
│   └── web/                    # Next.js 前端
│       ├── app/
│       │   ├── (dashboard)/    # 仪表盘页面（知识库、智能体、运行时日志）
│       │   └── chat/[publicId]/ # 公开聊天页面
│       └── components/         # UI 组件
├── docs/                       # 项目文档
├── evals/                      # 评测种子问题
├── infra/postgres/             # 数据库初始化脚本
├── docker-compose.yml          # Docker 本地服务编排
├── pnpm-workspace.yaml         # pnpm monorepo 配置
└── package.json                # 根项目脚本
```

## MVP 功能

- **知识库管理**：创建知识库，支持 PDF、DOCX、TXT、Markdown、网页 URL、手动笔记等多种来源
- **知识摄入管道**：解析 → 清洗 → 分块 → 向量化 → 存储，状态可追踪
- **混合检索**：向量搜索 + 关键词搜索 + 结果合并去重
- **智能体构建**：配置角色、系统提示词、模型参数、绑定知识库、引用策略
- **调试聊天**：实时问答，带引用标注和检索追踪面板
- **发布与分享**：一键发布为公开聊天页面
- **可观测性**：摄入状态监控、运行时追踪、模型用量统计

## 本地服务

启动 PostgreSQL 和 Redis：

```bash
docker compose up -d postgres redis
```

## 开发命令

```bash
# 前端开发
pnpm dev:web

# 后端开发
pnpm dev:api

# 前端测试
pnpm test:web

# 后端测试
pnpm test:api
```

## 环境变量

复制 `.env.example` 为 `.env`，按需配置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `database_url` | 数据库连接串 | `postgresql+psycopg://studio:studio@localhost:5432/studio` |
| `redis_url` | Redis 连接串 | `redis://localhost:6379/0` |
| `model_base_url` | 模型 API 地址 | `https://api.openai.com/v1` |
| `model_api_key` | 模型 API 密钥 | - |
| `chat_model` | 对话模型 | `gpt-4.1-mini` |
| `embedding_model` | 向量化模型 | `text-embedding-3-small` |

## 实施计划

详见 [`docs/superpowers/plans/2026-07-13-knowledge-fusion-agent-studio.md`](docs/superpowers/plans/2026-07-13-knowledge-fusion-agent-studio.md)。
