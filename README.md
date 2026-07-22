# Knowledge Fusion Agent Studio（知识融合智能体工作室）

多知识源 AI Agent 构建与管理平台，支持知识摄入、混合检索、RAG 问答、ReAct Agent、Tool Calling、Streaming、MCP 等核心能力。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Next.js、React、TypeScript |
| 后端 | FastAPI、Python、SQLAlchemy、Alembic |
| 数据库 | PostgreSQL + pgvector |
| 任务队列 | Redis + Celery |
| 模型层 | OpenAI 兼容 Chat / Embedding API（Function Calling） |
| 协议 | MCP（Model Context Protocol）、SSE（Server-Sent Events） |

## 功能概览

- **知识库管理**：创建知识库，支持 PDF、DOCX、TXT、Markdown、网页 URL、手动笔记等来源
- **知识摄入管道**：解析 → 清洗 → 分块 → 向量化 → 存储，状态机管理生命周期
- **混合检索**：向量检索 + 关键词检索融合去重排序，支持 CJK 分词
- **Agent 运行时**：ReAct 推理循环（Thought → Action → Observation → Final Answer），支持 Tool Calling
- **工具系统**：可扩展的 Tool Registry，内置知识库搜索、计算器、日期时间等工具，支持 JSON Schema 参数校验
- **流式输出**：基于 SSE 的 Streaming 响应，实时推送推理过程
- **MCP 集成**：实现 MCP Tool Server，支持 Tool Discovery 与 Tool Calling
- **Agent 发布**：一键发布为公开聊天页面
- **可观测性**：摄入状态监控、运行时追踪、模型用量统计

## 项目结构

```
FusionAgentStudio/
├── apps/
│   ├── api/                         # FastAPI 后端
│   │   ├── app/
│   │   │   ├── core/                # 配置管理
│   │   │   ├── db/                  # 数据库模型（10 张表）与会话
│   │   │   ├── routes/              # API 路由
│   │   │   │   ├── agents.py        # Agent CRUD + 发布
│   │   │   │   ├── chat.py          # RAG 调试聊天
│   │   │   │   ├── knowledge_bases.py # 知识库 CRUD
│   │   │   │   ├── sources.py       # 知识来源管理
│   │   │   │   ├── react_chat.py    # ReAct Agent 聊天
│   │   │   │   ├── react_streaming.py # ReAct SSE 流式
│   │   │   │   ├── mcp.py           # MCP 协议端点
│   │   │   │   ├── public_chat.py   # 公开聊天
│   │   │   │   └── runtime_logs.py  # 运行时日志
│   │   │   ├── schemas/             # Pydantic 模型
│   │   │   ├── services/
│   │   │   │   ├── agent/           # Agent 管理
│   │   │   │   ├── agent_runtime/   # 运行时引擎（RAG + ReAct + Streaming）
│   │   │   │   ├── ingestion/       # 摄入管道
│   │   │   │   ├── model_gateway/   # 模型网关
│   │   │   │   ├── retrieval/       # 混合检索
│   │   │   │   └── tools/           # 工具系统（Registry + 内置工具 + MCP）
│   │   │   └── workers/             # Celery 异步任务
│   │   ├── alembic/                 # 数据库迁移
│   │   └── tests/                   # 单元测试
│   └── web/                         # Next.js 前端
│       ├── app/(dashboard)/         # 仪表盘
│       ├── app/chat/[publicId]/     # 公开聊天
│       └── components/              # UI 组件
├── docs/                            # 项目文档
├── evals/                           # 评测种子数据
├── infra/postgres/                  # 数据库初始化
├── docker-compose.yml               # Docker 本地服务
└── pnpm-workspace.yaml              # Monorepo 配置
```

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/knowledge-bases` | GET/POST | 知识库列表/创建 |
| `/api/knowledge-bases/{id}` | GET/PATCH/DELETE | 知识库详情/更新/删除 |
| `/api/knowledge-bases/{id}/sources` | GET | 知识来源列表 |
| `/api/knowledge-bases/{id}/sources/file` | POST | 上传文件来源 |
| `/api/knowledge-bases/{id}/sources/web` | POST | 添加网页来源 |
| `/api/knowledge-bases/{id}/sources/note` | POST | 添加笔记来源 |
| `/api/sources/{id}/chunks` | GET | 查看分块 |
| `/api/sources/{id}/reindex` | POST | 重新索引 |
| `/api/sources/{id}` | DELETE | 删除来源 |
| `/api/agents` | GET/POST | Agent 列表/创建 |
| `/api/agents/{id}` | GET/PATCH/DELETE | Agent 详情/更新/删除 |
| `/api/agents/{id}/knowledge-bases` | POST/DELETE | 绑定/解绑知识库 |
| `/api/agents/{id}/publish` | POST | 发布 Agent |
| `/api/agents/{id}/unpublish` | POST | 取消发布 |
| `/api/agents/{id}/debug-chat` | POST | RAG 调试聊天 |
| `/api/agents/{id}/react-chat` | POST | ReAct Agent 聊天 |
| `/api/agents/{id}/react-chat/stream` | POST | ReAct SSE 流式聊天 |
| `/api/public/agents/{public_id}` | GET | 获取公开 Agent 信息 |
| `/api/public/agents/{public_id}/chat` | POST | 公开聊天 |
| `/api/mcp/agents/{id}/server-info` | GET | MCP 服务信息 |
| `/api/mcp/agents/{id}/tools` | GET | MCP 工具发现 |
| `/api/mcp/agents/{id}/tools/{name}/call` | POST | MCP 工具调用 |
| `/api/runtime-logs` | GET | 运行时日志列表 |
| `/api/conversations/{id}/traces` | GET | 对话追踪详情 |

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
```

## 测试

```bash
pnpm test:api    # 后端测试
pnpm test:web    # 前端测试
```

## 环境变量

复制 `.env.example` 为 `.env`，按需配置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `database_url` | PostgreSQL 连接串 | `postgresql+psycopg://studio:studio@localhost:5432/studio` |
| `redis_url` | Redis 连接串 | `redis://localhost:6379/0` |
| `model_base_url` | 模型 API 地址 | `https://api.openai.com/v1` |
| `model_api_key` | API 密钥 | - |
| `chat_model` | 对话模型 | `gpt-4.1-mini` |
| `embedding_model` | 嵌入模型 | `text-embedding-3-small` |
