# 金通科技
### 基于 LLM + MoE 架构的多维度 AI 智能股票分析与量化决策系统

> 一个可运行的真实数据 MVP：数据、模型、回退原因和证据覆盖情况都会显式展示，而不是把缺失数据包装成“实时结论”。
<p align="center">
  <img src="windows1.jpg" width="600">
</p>

## 快速启动

推荐使用 Docker Desktop，项目会同时启动 PostgreSQL、FastAPI 和前端：

```bash
cp .env.example .env
```

打开 `.env`，至少修改 `POSTGRES_PASSWORD` 和 `JWT_SECRET`，然后运行：

```bash
docker compose up --build
```

默认是 `DATA_MODE=real`，不会自动写入样例数据。真实模式只展示数据库中已经同步的记录；没有数据时页面显示空状态。需要查看固定 UI 演示数据时，使用前端 `npm run dev:demo`，它不连接后端。若确实需要后端样例账号和数据库快照，必须显式使用 `docker-compose.demo.yml`：

```bash
docker compose -f docker-compose.yml -f docker-compose.demo.yml up --build
```

演示账号为 `demo@jintong.example.com` / `Demo123456!`。不要在真实模式中设置 `DATA_MODE=demo` 或执行演示初始化脚本。

启动完成后访问：

- 前端：http://localhost:8080
- 后端 API 文档：http://localhost:8000/docs
- 后端健康检查：http://localhost:8000/

后端启动后可运行真实鉴权冒烟测试：

```bash
docker compose exec -T backend python scripts/smoke_auth.py
```

该脚本会创建一个临时审计账号，并验证密码哈希、注册、登录、JWT、过期令牌和画像更新流程。

注册、登录、JWT 鉴权和用户画像均由真实 FastAPI + PostgreSQL 后端处理，不是前端模拟。智谱 AI Key 是可选项；不配置时仍可使用账户和画像，但没有已验证行情数据时不会伪装成实时分析。

Docker 默认安装基础后端依赖。需要运行 AkShare 数据采集时，将 `INSTALL_DATA_DEPS=true` 后重新构建；这只安装 `backend/requirements-data.txt`。本地情绪模型仍属于完整 `backend/requirements.txt` 的独立可选能力。

### 功能依赖分层

- **无需外部 Key**：注册、登录、JWT、投资者画像、持仓记录、已有数据库内容和规则分析回退。
- **财经数据依赖**：AkShare 用于行情、新闻、财报和行业数据采集；CNInfo 财报接口还需要配置请求头缓存。
- **AI 分析依赖**：智谱 AI 只需要一组 `ZHIPU_API_KEY`，轻量 SDK 已包含在基础后端镜像中。未配置时不会拖垮后端，系统会显示“未配置”并使用规则回退。
- **本地情绪模型**：需要 Transformers/PyTorch 和模型文件，属于可选增强能力。

可在 `GET /api/v1/system/capabilities` 查看当前实例的能力状态；前端首页也会显示同一份状态。

阶段 3 的 AI 分析为可选能力。配置 `ZHIPU_API_KEY` 后重建后端，分析结果会记录模型、分析模式、数据覆盖和回退专家；没有 Key 或调用失败时，结果会明确标记为本地规则回退，不会伪装成 LLM 输出。可先运行：

```bash
docker compose exec backend python scripts/check_zhipu.py
```

启用 AkShare 后，先用受限试验接口验证 3 至 5 只股票，不要直接运行全市场同步：

```bash
docker compose exec backend python scripts/sync_minimal_real.py 000001 000333 000651
```

也可以通过已登录的 `POST /api/v1/data/sync/minimal-real` 调用同一流程。返回的同步日志会分别记录报价、K 线、公司资料、财报和新闻的数量、来源及失败原因。

前端本地开发模式：

```bash
cd frontend
npm install
npm run dev
```

前端默认连接 `http://localhost:8000/api/v1`。仅查看界面和示例数据时可运行 `npm run dev:demo`，页面会明确标注演示模式。

## 环境变量

根目录 `.env` 供 Docker Compose 使用，`backend/.env` 供脱离 Docker 单独启动后端时使用。这些文件包含本机密码和 API Key，已被 Git 忽略；仓库中只提交 `.env.example`。

项目统一使用数据库名 `stockai`、数据库外部端口 `5433`、后端端口 `8000`、开发前端端口 `5173`、Docker 前端端口 `8080`。容器内部仍使用 PostgreSQL 标准端口 `5432`。不要复用旧仓库历史中出现过的 API Key。

## 项目简介
金通科技是一款面向 A 股市场的深度智能分析平台。系统打破了传统资讯聚合的模式，构建了由 5 大领域专家 LLM 组成的决策矩阵。通过整合实时盘面数据、深度财务因子、社交媒体舆情及宏观经济环境，为用户提供“有理、有据、透明”的投资决策支持。

项目核心解决“信息过载”与“决策主观”的问题，通过 Agentic Workflow 将碎片化数据转化为可执行的投资交易方案。

## 我完成的工程工作

这个版本不只是页面原型，而是对原团队项目进行了真实数据化、稳定性和可观测性改造：

- 将运行默认切换为 `DATA_MODE=real`，并建立 Demo 数据隔离开关；真实模式不会自动播种演示账号、行情或分析快照。
- 打通 AkShare 行情、K 线、新闻、行业、东方财富 F10/财务数据的同步与来源记录，页面显示 `source`、抓取时间和同步状态。
- 重构分析结果状态协议，增加 `data_source_status` 和 `ai_analysis_status`，区分 LLM 成功、规则回退、完全失败和限流原因。
- 修复重复分析导致的快照唯一约束冲突，使同一股票连续分析可以安全更新已有快照。
- 修复无画像注册时金额字段为 `None` 导致 HTTP 500 的边界问题。
- 将专家分析改为单密钥顺序调用并保留节流/重试，避免 5 个并发请求主动触发智谱 `429/1305` 限流；同时切换到更稳定的 `glm-4-flash` 默认配置。
- 在前端加入规则回退横幅、来源/更新时间面板、证据缺失提示和专家回退原因，避免把规则文本误认为 LLM 结论。
- 修复宏观报告缺失指数时显示 Python `None` 的问题，增加报告日期、覆盖量和缺失字段元数据。
- 为情绪分析增加明确标记的词典回退：未安装 Transformers/PyTorch 时仍可生成可解释结果，但不会冒充模型推理。
- 为每日同步和排名任务增加超时边界，避免页面无限停留在“生成中”。
- 增加注册、鉴权、双重分析、限流回退、无 Demo 数据、财务同步和量化因子等回归脚本。

## 已验证的关键结果

在真实模式 `jintong-real` 环境中已验证：

- 000001（平安银行）连续分析两次均成功完成，第二次不再触发快照 `UniqueViolation`。
- 智谱模型切换和顺序请求后，最新真实分析的五位专家均可走 LLM；发生供应商限流时响应会明确标记回退，而不是静默伪装。
- 注册请求不带画像仍返回成功。
- 真实数据库不存在 `demo@jintong.example.com` 或 `demo_seed` 数据。
- 前端 TypeScript/Vite 构建通过，Docker Compose 的前端、后端和 PostgreSQL 健康检查通过。

## 测试与验收命令

```bash
# 前端静态构建
cd frontend && npm ci && npm run build

# 后端容器内运行回归脚本
docker compose -p jintong-real exec -T backend python scripts/smoke_auth.py
docker compose -p jintong-real exec -T backend python scripts/test_register_without_profile.py
docker compose -p jintong-real exec -T backend python scripts/test_double_analysis_000001.py
docker compose -p jintong-real exec -T backend python scripts/test_llm_rate_limit_fallback.py
docker compose -p jintong-real exec -T backend python scripts/test_no_demo_data_in_real_mode.py
```

## 核心架构
系统采用“决策融合层（LLM + MoT）”架构，实现专家级协同分析：

用户画像系统：基于前景理论与 Grable & Lytton 量表，量化投资者的损失厌恶与风险敏感度（RSI指数）。

五大专家阵列：

新闻专家：识别政策噪音，区分短期情绪与长期经营逻辑。

股票数据专家：多周期 K 线、资金流向、Beta/Sharpe 率及估值偏离度分析。

宏观面专家：分析全球地缘政治与国内会议政策的传导路径。

财务数据专家：深度穿透利润表、资产负债表，计算 ROE/PE/PB 等质量因子。

公司基本面专家：拆解商业模式、申万行业地位及股权治理结构。

情绪预测中心：集成 RoBERTa 与 FinBERT 双模型，实时监控股吧评论与媒体情绪趋势。

投资总分析师：综合专家意见与用户个性，生成包含买入、仓位、止盈止损、回本策略的全生命周期方案。

## 核心功能模块
**1. 智能盘后复盘 & 排行榜**
自动化流水线：支持手动触发和后台任务轮询；部署环境可通过外部定时器触发同步。结合当日交易数据、即时新闻进行扫描。

多维评分体系：根据专家打分生成“金通推荐榜”，支持透明化查阅每项打分依据。

信噪背离预警：当“数据驱动专家”与“情绪驱动专家”信号相反时，系统自动红灯预警。

**2. 个性化风险画像 (RSI Model)**
量化建模：通过 4 维度矩阵将文本问卷转化为 [0, 1] 连续型风险指数。

千人千面：根据保守、稳健、进取、激进四种画像，动态调整投资建议中的仓位占比与风险提示权重。

**3. 情绪指数与策略对冲**
舆情监控：实时爬取东方财富股吧数据，进行 NLP 情感极性分析。

策略应用：构建“情绪水平-基本面价值”象限图。针对“多头排列”、“过度反应”、“转折预判”等场景输出特定决策文字。

**4. 深度财务与量化因子**
因子看板：自动化计算质量因子（ROE/ROA）、成长因子（营收同比）、风险因子（资产负债率）。

横纵向对比：实现公司近三年财务数据的纵向趋势分析及与行业龙头的横向比对。

## 可视化交互
动态 K 线图：支持日/周/月线缩放与拖拽，集成成交量柱状图与交互式数据点查询。

独立宏观大盘：一键生成“今日宏观分析报告”，涵盖 GDP/CPI 趋势、美联储政策影响及 A 股风格轮动建议。

## 技术实现细节
后端引擎：Python + FastAPI，后台任务负责数据同步与分析；同一智谱 Key 使用顺序调用、节流和重试，降低供应商限流风险。

数据采集：AkShare 接入。

模型选型：

LLM: ChatGLM 系列 (Zhipu AI)

NLP: Fearao/RoBERTa_based_on_eastmoney_guba_comments & finbert-tone-chinese

前端方案：React + TypeScript，基于数据驱动的状态渲染，支持真实模式和显式标记的 UI 演示模式。


**免责声明**
本系统仅供学术交流与科研使用，所提供的投资建议均基于 AI 模型预测，不构成任何形式的投资合同或法律承诺。入市有风险，投资需谨慎。

## 项目说明

本项目最初由团队共同完成，当前仓库是在原团队项目基础上整理、清理敏感信息并继续维护的个人版本。原始贡献归相应团队成员所有。
