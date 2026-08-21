# 金通科技项目交付与后续开发说明

更新日期：2026-08-19

## 1. 最终目标

将团队项目 `JinTong-Technology` 整理为一个可由他人复现、可持续开发、可发布到个人 GitHub 的 A 股研究与投资决策平台。

目标不是制作“看起来有数据”的静态演示，而是：

- 前端、后端、数据库能一键启动；
- 用户可以真实注册、登录、保存自己的画像和持仓；
- 行情、财报、新闻等数据有明确、可追溯的数据来源与更新时间；
- AI 分析有可用的真实模型/API 配置和失败提示；
- 没有 Key、网络或数据源不可用时，页面明确说明功能不可用，不能把样例或旧数据伪装成实时结论；
- 清理敏感信息后放入一个全新的个人 GitHub 仓库。

当前项目适合作为“本地运行的 MVP / 工程作品”，尚不能称为可用于真实投资判断的平台。

## 2. 当前代码位置与来源

- 本地项目：`/Users/liyidan/Downloads/JinTong-Technology-init`
- 团队原始仓库：https://github.com/caiziyi1313113/JinTong-Technology
- 后续应新建个人仓库并推送干净代码；不要直接 Fork 原仓库，因为原历史可能包含旧密钥。
- README 中应保留团队项目来源，并写明个人完成的前端改版与工程化整理。

## 3. 当前运行状态（已验证）

Docker Compose 已成功启动并验证：

| 服务 | 地址 | 当前状态 |
|---|---|---|
| 前端 Nginx | http://localhost:8080 | Docker healthcheck 已修复并健康 |
| FastAPI 后端 | http://localhost:8000 | 健康 |
| Swagger API 文档 | http://localhost:8000/docs | 可访问 |
| PostgreSQL | localhost:5433 | 健康 |

常用命令：

```bash
cd /Users/liyidan/Downloads/JinTong-Technology-init
docker compose up --build -d
docker compose ps
docker compose logs --tail=120 backend
docker compose down
```

根目录 `.env` 已存在且被 `.gitignore` 忽略。绝对不要将其中的数据库密码、JWT 密钥或未来的 API Key 提交到 GitHub。

## 4. 已完成工作

### 4.1 前端

- 完成浅色、信息密度更高的前端改版。
- 页面包括：首页、登录/注册、选股评审、持仓跟踪、单股分析、宏观分析、投资者画像。
- `npm run build` 和 `npm run build:demo` 已通过。
- `npm run dev` 连接真实后端；`npm run dev:demo` 是前端固定数据预览模式，不能视为真实系统。
- Docker 前端使用 Nginx 代理 `/api/v1` 到 FastAPI，并支持 SPA 路由刷新。

### 4.2 后端与账户

- FastAPI + PostgreSQL + Python 3.11 Docker 环境已整理。
- 注册、登录、bcrypt 密码哈希、JWT、用户身份读取、投资者画像读写均已实现。
- 后端冒烟测试 `backend/scripts/smoke_auth.py` 已通过，覆盖：注册、重复注册、密码校验、JWT、过期 Token、画像、问卷和资金约束。
- 前端在 Token 过期时会清理本地登录状态。

### 4.3 环境与安全

- 数据库名统一为 `stockai`。
- Docker 暴露 PostgreSQL 为 `5433`，避免常见的本机 `5432` 冲突。
- 后端端口 `8000`，Docker 前端端口 `8080`，前端本地开发端口 `5173`。
- `DATABASE_URL`、`JWT_SECRET` 改为必须从环境变量读取；代码不保留默认真实凭据。
- 已补充根目录 `.env.example`、`backend/.env.example` 和 `环境配置.md`。
- 密钥扫描和 `.gitignore` 检查已做过一次；正式发布前必须再做一次。

### 4.4 Docker

- `docker-compose.yml` 已包含 `db`、`backend`、`frontend` 三个服务。
- 数据库、后端和前端均有健康检查。
- 前端健康检查已改为 `127.0.0.1`，修复 Alpine 容器中 `localhost` 可能解析到 IPv6 导致的误报。

### 4.5 外部能力状态

- 新增接口：`GET /api/v1/system/capabilities`。
- 首页显示当前实例的能力状态。
- 无智谱 Key 时，后端不会崩溃；会显示 AI 未配置，并走已有的规则分析代码路径。
- 这只是“系统可降级运行”，不是“AI 已真实可用”。

## 5. 当前样例数据：必须诚实标识

为方便本地浏览，Docker 启动时会运行 `backend/app/services/demo_seed.py` 的初始化逻辑，创建：

- 演示账号：`demo@jintong.example.com`
- 演示密码：`Demo123456!`
- 股票代码与名称：000001 平安银行、000333 美的集团、000651 格力电器、002415 海康威视、002594 比亚迪。
- 行情、周线、报价、基本面、财报、新闻、宏观资料、排名、持仓、交易、分析和交易计划。

### 数据真实性结论

| 内容 | 当前性质 |
|---|---|
| 股票代码和名称 | 真实 A 股代码/名称 |
| 登录、数据库读写、画像、持仓功能 | 真实可运行功能 |
| 样例行情价格、成交量、K 线 | 人工生成，非真实历史或实时行情 |
| 样例财报数值、基本面描述、新闻文本 | 人工生成，非公司真实披露 |
| 样例排名、专家评分、交易建议、持仓 | 人工生成，不能作为投资依据 |
| 当前 AI 分析 | 无智谱 Key 时为规则回退，不是 LLM 实时生成 |

已经采取的防误导措施：

- 首页能力区显示“本地样例数据”，明确说明不是实时数据；
- 登录后工作台顶栏显示“本地样例数据”；
- 初始化记录带 `demo_seed` 来源标记；
- README 和环境配置文件明确说明样例数据性质。

仍建议后续进一步实现：每一个行情/财报/新闻/分析详情都显示 `source`、`更新时间`、`数据状态（真实/样例/过期/失败）`。

## 6. 当前未接通的真实能力

### 6.1 行情与财经数据

代码中已有 AkShare 采集服务：`backend/app/services/data_ingest/akshare_service.py`。

当前 Docker 使用 `backend/requirements-core.txt`，未安装 AkShare，因此当前实例没有真实行情、财报或新闻同步能力。完整依赖在 `backend/requirements.txt`，但是否能稳定运行、各接口是否仍有效，尚未在本机逐项验证。

后续目标：

1. 先确定允许使用且稳定的数据来源（AkShare 是公开数据聚合工具，不是正式 SLA 数据服务）。
2. 安装并锁定所需依赖。
3. 只选择少量股票做真实同步试验。
4. 保存每条数据的来源、抓取时间、原始字段和失败原因。
5. 在界面显示“最后更新时间”和“非交易时段/数据源失败”的状态。
6. 写自动化接口测试，确认数据不是空的、旧的或错误映射。

### 6.2 CNInfo / 巨潮资讯财报

项目中有 CNInfo 相关逻辑，但当前未配置必要请求头：

- `CNINFO_ACCEPT_ENCKEY`
- `CNINFO_COOKIE`
- 可选 `CNINFO_REFERER`、`CNINFO_USER_AGENT`

没有配置时应显示未配置并跳过，不能以样例财报替代真实披露。接入前还需要确认请求频率、合法性和稳定性。

### 6.3 智谱 AI

当前只需要一组环境变量：

```dotenv
ZHIPU_API_KEY=你的单个智谱Key
```

不需要旧项目中多个专家各自一组 Key。`zai-sdk` 已在核心依赖中。

接入后必须完成：

1. 用单个 Key 验证一只股票的端到端分析；
2. 记录模型名、调用时间、输入数据时间、请求失败原因；
3. 设置超时、限流与成本上限；
4. 将模型输出明确标注为“AI 辅助分析，不构成投资建议”；
5. Key 缺失或调用失败时，前端显示不可用/失败，不能将旧样例伪装为新结果。

### 6.4 本地情绪模型

Transformers/PyTorch 和模型文件当前未安装。该功能应在模型实际下载、加载和样本验证后才可标为可用。

## 7. 后续工作清单（推荐顺序）

### 阶段 A：停止依赖“假数据”

- [ ] 将 `SEED_DEMO_DATA` 默认值改为 `false`，或将演示数据完全隔离到独立 `demo` profile。
- [ ] 在全部涉及数据的页面显示来源、更新时间与状态。
- [ ] “没有实时数据”时显示空状态和下一步操作，不显示仿真价格。
- [ ] 保留前端 `npm run dev:demo` 仅用于 UI 截图/界面开发，不作为完整系统演示。
- [ ] 重新审查所有 `frontend/src/demoData.ts` 和 `backend/app/services/demo_seed.py` 入口，保证不会在真实模式混入。

### 阶段 B：真实数据最小闭环

- [ ] 明确首个真实数据源与使用边界。
- [ ] 在 Docker 中增加可选的 `requirements-data.txt` 或单独数据同步服务，不要默认安装沉重的完整 AI 依赖。
- [ ] 选 3-5 只股票，验证股票列表、历史 K 线、最新报价、财报和新闻。
- [ ] 为每个数据表增加/核验来源、抓取时间、交易日、数据版本。
- [ ] 后端提供最近更新时间、同步任务状态、失败详情 API。
- [ ] 前端显示数据新鲜度和来源链接。

### 阶段 C：真实分析闭环

- [ ] 配置一组智谱 Key 并进行真实调用测试。
- [ ] 输入必须来自已验证的真实数据，而不是 seed 数据。
- [ ] 保存分析版本、模型、输入快照和原始引用证据。
- [ ] 验证无 Key、网络失败、限流、超时时的 UI 行为。
- [ ] 对排名和分析建立回测/人工核验方案；未经验证不能宣称推荐有效。

### 阶段 D：质量与发布

- [ ] 执行前端正式构建和演示构建。
- [ ] 执行后端语法、接口、注册登录和数据同步冒烟测试。
- [ ] 增加针对真实数据源的可重复集成测试（应允许网络不可用时跳过）。
- [ ] 再次执行敏感密钥扫描与 `.gitignore` 检查。
- [ ] Docker 从全新 volume 启动并完成端到端验证。
- [ ] 更新 README：技术架构、真实/演示模式、数据来源、API 配置、免责声明、截图、团队来源和个人改版说明。
- [ ] 初始化全新 Git 仓库，提交干净代码，推送到新的个人 GitHub 仓库。

### 阶段 E：部署（最后再做）

- [ ] 演示前端可部署为静态页面，但必须明确为界面演示。
- [ ] 完整真实系统需要后端、PostgreSQL、环境变量和数据同步任务托管。
- [ ] 部署前配置 HTTPS、CORS、生产 JWT 密钥、数据库备份、日志和访问控制。

## 8. 关键配置

根目录 `.env.example` 是模板；本地 `.env` 是实际配置，不能提交。

```dotenv
POSTGRES_USER=postgres
POSTGRES_PASSWORD=replace-with-a-local-database-password
POSTGRES_DB=stockai
POSTGRES_PORT=5433
JWT_SECRET=replace-with-a-random-secret-at-least-32-characters
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:8080

# 可选：AI 分析
ZHIPU_API_KEY=
ZHIPU_ALLOW_CROSS_ROLE_KEY_FALLBACK=true

# 本地样例数据；向真实模式迁移时应关闭。
SEED_DEMO_DATA=true
DEMO_USER_EMAIL=demo@jintong.example.com
DEMO_USER_PASSWORD=Demo123456!
```

## 9. 关键文件索引

| 目的 | 文件 |
|---|---|
| Docker 编排 | `docker-compose.yml` |
| 后端入口与自动初始化 | `backend/app/main.py` |
| 环境变量定义 | `backend/app/core/config.py` |
| 运行能力状态 API | `backend/app/api/routes/system.py` |
| 样例数据初始化 | `backend/app/services/demo_seed.py` |
| 手工初始化脚本 | `backend/scripts/seed_demo.py` |
| 登录功能 | `backend/app/api/routes/auth.py` |
| 登录/画像冒烟测试 | `backend/scripts/smoke_auth.py` |
| 数据采集服务 | `backend/app/services/data_ingest/akshare_service.py` |
| 前端 API 客户端 | `frontend/src/api.ts` |
| 首页能力状态 | `frontend/src/pages/Home.tsx` |
| 工作台样例数据标识 | `frontend/src/components/Header.tsx` |
| 前端固定样例 | `frontend/src/demoData.ts` |
| 项目文档 | `README.md`、`环境配置.md` |

## 10. 交接给下一位开发助手的首要请求

建议直接这样描述任务：

> 请基于 `CODEX_PROJECT_HANDOFF_ZH.md` 继续开发。目标是将当前本地 MVP 变成数据来源清晰、可真实使用的研究平台，而不是展示用假数据。先审计所有样例数据入口，设计并实现“真实数据模式”和“UI 演示模式”的严格隔离；然后接入并验证第一条真实数据源，保留来源、更新时间、失败状态，并完成端到端测试。不要提交 `.env` 或任何真实密钥，不要影响无关项目或 minikube。

## 11. 2026-08-19 对话交接记录

本轮目标：继续把本地 MVP 变成真实可用的 A 股研究平台，严格隔离真实数据与 UI 演示数据，保留来源/更新时间/失败状态，智谱分析真实可用或明确失败；不提交 `.env`、数据库密码、JWT 密钥或 API Key，不影响无关项目和 minikube。

### 已完成

- 阶段 1：已实现 `DATA_MODE=real|demo`；真实模式不会初始化 demo；演示需显式使用 `docker-compose.demo.yml`。当前非敏感开关为 `DATA_MODE=real`、`INSTALL_DATA_DEPS=true`、`SEED_DEMO_DATA=false`。
- 阶段 2：AkShare 位于 `backend/requirements-data.txt`；已有受限同步 API `POST /api/v1/data/sync/minimal-real` 和脚本 `backend/scripts/sync_minimal_real.py`；行情/K 线保留 source/fetched_at；真实验收曾通过 quotes=3、history=166、financials=496、documents=31、demo rows=0。
- 阶段 3：智谱 Key 已配置但不可读取/输出；`docker compose -p jintong-real exec backend python scripts/check_zhipu.py` 已成功，SDK 0.2.2，默认模型 `glm-4.7-flash`；分析保存 `llm_meta`，前端区分 `llm` 与 `rules_fallback`。

### 当前运行

Compose 项目名为 `jintong-real`。前端 `http://localhost:8080`，后端 `http://localhost:8000`，PostgreSQL `localhost:5433`。旧项目曾占用 8000，已执行 `docker compose -p jintong-technology-init down`；不要使用 `down -v`。

演示账号（仅 demo 显式启用时存在）：`demo@jintong.example.com` / `Demo123456!`。真实模式无此用户时从注册页创建个人账号。

### 错误与修复

在 `query?symbol=000001` 重复分析时出现 PostgreSQL `UniqueViolation`：约束 `uq_ak_snapshot_key_date_layer_symbol`，键为 `(peer_growth, 2026-08-19, raw, 000001)`。结论：与智谱 Key 无关，是快照重复写入没有数据库级幂等保护。

已修改 `backend/app/services/data_ingest/akshare_service.py` 的 `_upsert_ak_snapshot`：PostgreSQL 使用 `pg_insert(...).on_conflict_do_update`，冲突时更新 `source`、`summary`、`payload`；非 PostgreSQL 保留兼容路径，不删除已有数据。`py_compile` 已通过，后端镜像已成功重建且容器已启动。

### 下一次验证

执行 `docker compose -p jintong-real ps` 和 `docker compose -p jintong-real exec backend python scripts/verify_real_data.py`；再在 `http://localhost:8080/query?symbol=000001` 连续点击两次“重新分析”，确认第二次不再出现 `UniqueViolation`，并确认页面显示真实模型成功或清晰的失败状态。随后补同一股票连续同步/分析两次的自动化回归测试。

### 注意事项与下一步

- 严禁打印/提交 `.env` 中的 `ZHIPU_API_KEY`、`POSTGRES_PASSWORD`、`JWT_SECRET` 或登录 Token。
- 不要停止/修改 minikube 或无关项目，不要删除 PostgreSQL volume。
- 后续顺序：完成双跑验证和回归测试；审计分析输入确保无 demo 行；增加数据源失败/超时/限流状态；做前端构建、后端测试、密钥扫描和全新 volume 验收；最后再建个人 GitHub 仓库。
