# Knowledge Fusion Agent Studio（知识融合智能体工作室）

## 项目描述

基于 Python 构建 AI Agent 学习与实验平台，实现 ReAct Agent、Tool Calling、RAG、MCP、Memory、Streaming 等核心能力，覆盖 Agent 生命周期及工程化实践。

## 技术栈

Python、FastAPI、Next.js、TypeScript、PostgreSQL + pgvector、Redis、Celery、SQLAlchemy、Alembic、OpenAI API、MCP、Function Calling、Streaming、RAG

## 项目亮点

- 实现 ReAct Agent 主循环，支持 Thought → Action → Observation → Final Answer 推理流程，基于 OpenAI Function Calling 驱动工具调用决策，最大迭代次数可配置。
- 基于 OpenAI Function Calling 封装 Tool Registry（工具注册中心），支持动态工具注册、JSON Schema 参数校验（类型校验、枚举约束、默认值填充），提供统一的 `to_openai_schema()` 格式转换。
- 内置多种 Agent Tool：知识库混合检索工具（向量 + 关键词融合）、数学计算器工具、日期时间工具，支持按 Agent 动态绑定知识库搜索。
- 基于 PostgreSQL + pgvector 实现 Agent Memory，Conversation、Message、RuntimeTrace 完整持久化，支持对话历史追溯与运行时追踪回放。
- 基于 FastAPI + SSE（Server-Sent Events）实现 Agent Streaming 输出，流式推送 thought / action / observation / final_answer / done 等事件，支持前端实时渲染 Agent 推理过程。
- 集成 MCP Tool Server，实现 Tool Discovery 与 Tool Calling，遵循 Model Context Protocol 规范，对外暴露工具发现与调用接口，Agent 可注册为 MCP 服务供外部客户端消费。
- 实现完整 RAG 流程，覆盖文本解析（PDF/DOCX/TXT/Markdown/网页/笔记 6 种来源）→ 清洗 → 分块（可配置重叠窗口）→ Embedding 向量化 → pgvector IVFFlat 索引存储 → 混合检索（向量余弦相似度 0.7 + 关键词 CJK n-gram 0.3 融合去重）。
- 封装 OpenAI 兼容模型网关（Model Gateway），抽象 Chat / Embedding / ChatWithTools 接口，ChatMessage 支持 tool_calls / tool_call_id 完整 Function Calling 语义，实现模型层与业务层解耦。
- 基于 Redis + Celery 实现异步知识摄入任务队列，支持大文件/多来源并行处理，状态机管理 `pending → indexing → indexed/failed` 生命周期。
- 编写 20 个测试文件（50+ 用例），覆盖 Tool Registry、内置工具、MCP Server、混合检索合并、提示构建、引用生成、知识库/来源/Agent CRUD、ReAct 聊天等核心模块。

## 项目结构

```
FusionAgentStudio/
├── apps/
│   ├── api/                              # FastAPI 后端
│   │   ├── app/
│   │   │   ├── core/config.py            # 配置管理
│   │   │   ├── db/                       # ORM 模型 + 会话管理（10 张表）
│   │   │   ├── routes/                   # API 路由（含 react-chat / SSE streaming / MCP）
│   │   │   ├── schemas/                  # Pydantic 数据模型
│   │   │   ├── services/
│   │   │   │   ├── agent/                # Agent CRUD + 发布管理
│   │   │   │   ├── agent_runtime/        # 运行时引擎
│   │   │   │   │   ├── react_agent.py    # ReAct 主循环
│   │   │   │   │   ├── react_streaming.py # ReAct 流式版本
│   │   │   │   │   ├── react_chat_service.py # ReAct 聊天服务
│   │   │   │   │   └── ...               # chat / prompt / citations
│   │   │   │   ├── ingestion/            # 摄入管道（parsers/cleaning/chunking/indexer）
│   │   │   │   ├── model_gateway/        # 模型网关（OpenAI 兼容 + Function Calling）
│   │   │   │   ├── retrieval/            # 混合检索（hybrid merge）
│   │   │   │   └── tools/                # 工具系统
│   │   │   │       ├── types.py          # ToolDefinition / ToolParameter / ToolCall
│   │   │   │       ├── registry.py       # ToolRegistry（注册/校验/执行）
│   │   │   │       ├── builtin.py        # 内置工具（搜索/计算器/日期时间）
│   │   │   │       └── mcp_server.py     # MCP Tool Server
│   │   │   └── workers/                  # Celery 异步任务
│   │   ├── alembic/                      # 数据库迁移
│   │   └── tests/                        # 20 个测试文件
│   └── web/                              # Next.js 前端
│       ├── app/(dashboard)/              # 仪表盘
│       ├── app/chat/[publicId]/          # 公开聊天
│       └── components/                   # UI 组件
├── docs/                                 # 项目文档
├── evals/                                # 评测种子数据
├── docker-compose.yml                    # Docker 本地服务
└── pnpm-workspace.yaml                   # Monorepo 配置
```

## 核心 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/agents/{id}/react-chat` | POST | ReAct Agent 同步聊天（含 Tool Calling） |
| `/api/agents/{id}/react-chat/stream` | POST | ReAct Agent SSE 流式聊天 |
| `/api/mcp/agents/{id}/server-info` | GET | MCP 服务端信息 |
| `/api/mcp/agents/{id}/tools` | GET | MCP Tool Discovery（工具发现） |
| `/api/mcp/agents/{id}/tools/{name}/call` | POST | MCP Tool Calling（工具调用） |
| `/api/agents/{id}/debug-chat` | POST | 原有 RAG 调试聊天 |
| `/api/public/agents/{public_id}/chat` | POST | 公开聊天 |

## 本地运行

```bash
# 启动基础服务
docker compose up -d postgres redis

# 安装依赖
pnpm install
cd apps/api && pip install -e .

# 数据库迁移
cd apps/api && alembic upgrade head

# 开发模式
pnpm dev:api    # 后端 http://localhost:8000
pnpm dev:web    # 前端 http://localhost:3000

# 测试
pnpm test:api
pnpm test:web
```

## 环境变量

复制 `.env.example` 为 `.env`，配置模型 API：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `database_url` | PostgreSQL 连接串 | `postgresql+psycopg://studio:studio@localhost:5432/studio` |
| `redis_url` | Redis 连接串 | `redis://localhost:6379/0` |
| `model_base_url` | 模型 API 地址 | `https://api.openai.com/v1` |
| `model_api_key` | API 密钥 | - |
| `chat_model` | 对话模型 | `gpt-4.1-mini` |
| `embedding_model` | 嵌入模型 | `text-embedding-3-small` |
