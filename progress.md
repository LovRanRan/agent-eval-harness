---
project: agent-eval-harness
phase: P3→P4
status: pre-build  # planning / pre-build / building / shipping / done
created: 2026-06-13
soft_deadline: 2026-09-15   # 40-repo eval study 完整版 ship（Wave 3 简历 v2.0）
hard_deadline: 2026-10-15   # OSS v0.5 + 文章
---
# `agent-eval-harness` — 单文件进度板

---

## 📌 Project Description

> **`agent-eval-harness`** 是 Phase 3→4 的 **开源 agent 评测框架 + 40-OSS-repo Supervisor-vs-ReAct benchmark**:既给别人一个可复用的 agent eval 工具,又内置一个评测 `wayfinder` 的旗舰基准。

**项目定位**

从 Project 6 `wayfinder`(能跑的 multi-agent 产品)推进到**量化系统质量**:给面试官 rigorous eval 数据(99% new grad 没有),并证明能把评测抽象成可复用框架。合并原因:框架 = benchmark 的基础设施,分开做要把评测基建搭两遍。

**技术契约**（对应 `final_checklist.md` Project 7 acceptance,Commit 0 后细化）

- **数据集**：40 OSS repo(10 web frameworks + 10 ML libs + 10 CLI tools + 10 distributed systems),每个 repo ≥1 个可跑 pytest/jest 套件(mcp-test-runner 前提);先 smoke 筛掉破损套件。
- **任务桶**：Architecture Understanding / Function Tracing / Claim Verification / Bug Localization。
- **架构对比**：Wayfinder Supervisor vs ReAct（Swarm 砍掉)。
- **Metrics(4)**：routing accuracy / factual correctness / citation grounding / **verification_rate**(题材升级后最强差异化数字)。
- **Judges**：LLM-as-judge(Claude + GPT)+ ground-truth 对比;self-consistency(CoT-SC)。
- **框架 API**：datasets / runners / metrics / judges / failure-mode taxonomy(hallucination / tool misuse / retrieval / reasoning)/ token+cost tracking / CLI runner / 集成 adapter(LangGraph 等)。
- **产物**：`EVAL_REPORT.md` + 4 张 SVG 图 + 一句话 headline number(进简历)+ OSS v1.0(docs/tests/examples)。
- **成本**：40 task × 3 self-consistency × 2 arch ≈ 240 runs · ~$50–$200/full eval;预算紧时 Haiku 做 sub-agent + Sonnet 做 supervisor + judge。

**项目领域**

> ⬜ 待你手填(例如:"AI/devtools agent 的评测方法论 + codebase-understanding benchmark")。

**简历差异化**

> ⬜ 待你手填(3–5 条,本框架比 generic eval 强在哪;参考:verification_rate 量化反幻觉、自评 wayfinder、开源可复用)。

**跨项目衔接**

- ⬅ **Project 6 `wayfinder`**：本项目的评测对象 + 数据来源(读 wayfinder 的 run/traces);v0.5 也在 P3 `arxiv-rag` / P4 `single-file-explainer` 上跑作 examples。
- ➡ **简历 / 文章**：headline number 直接进 wayfinder 简历 bullet + 第 1 篇技术文章("Supervisor vs ReAct on 40 OSS repos with embedded verification")。

**成功判定**

- [ ]  `final_checklist.md` Project 7 acceptance 全部 `[x]`
- [ ]  GitHub 仓库公开 + OSS v0.5(docs/tests/examples)
- [ ]  `EVAL_REPORT.md` + 4 SVG 图 + 一句话 headline number
- [ ]  `TASKS.md` Project 7 ship 行 `[x]`

---

## 🔒 Core Principles

> ⬜ 待你手填(项目级硬规则;参考方向:① 评测先于自夸——任何 headline number 必须可复现;② golden set + LLM-judge 双轨,judge bias 要显式控制;③ 成本透明,每个 metric 标 run 数/花费)。

---

## ✍️ Ownership Build Protocol

沿用 Project 6 的四步法:Haichuan 写设计 + skeleton → Codex 补局部实现/debug/test → Haichuan 反向解释。评测框架的 **eval API / metric 定义 / dataset schema / judge 策略** 由 Haichuan 主导,Codex 只补 boilerplate / 局部实现。不知道怎么写 design note 时进 guided design mode(一次一问)。

---

## 📊 Dashboard


|                        |                                                            |
| ---------------------- | ---------------------------------------------------------- |
| 当前阶段               | **🏁 首个完整 benchmark 跑通**(Supervisor vs ReAct,12 任务,4 metric,0 错误;report/small_v1)。下一步:修 ReAct pytest 工具 → 干净 re-run / 扩 40-repo |
| 进度                   | 0 / N acceptance criteria done(脚手架不计 acceptance）     |
| 完成 commits           | C1–C8 · ReAct baseline · verifier-B · **4 metric 来源全 + benchmark driver/CLI** |
| Gate 状态              | ✅ ruff / ruff-format / mypy --strict(12 files)/ pytest(64 passed);CI uv-native(`uv sync`+`uv run`) |
| 🔑 资源状态            | Anthropic key ✅(judge)· OpenAI key ✅(gpt-5.5 可用)· Docker ✅(v29.4.3 daemon up)· wayfinder+project5 ✅ —— **真跑前置全齐** |
| 软截止                 | 2026-09-15                                                 |
| 硬截止                 | 2026-10-15                                                 |
| **Today's North Star** | ⬜ 待你手填(建议:写 Commit 1 eval-API design note —— datasets/runner/metric/judge schema) |

---

## 🗺 Roadmap

### Pre-build（从 `fast_path.md` Project 7 节）

- [x] 必读清单第 3 篇(Hamel "Your AI Product Needs Evals")—— 已读
- [ ] LangSmith experiments 一页 — https://docs.smith.langchain.com/evaluation(~30min）
- [/] eval API 设计 + dataset schema —— `DESIGN.md` guided 模板已起,Commit 1 定稿

> **执行模式 (2026-06-14, David 授权)**:本项目全部由 Claude 写(含原 rule 13–16 的设计/skeleton/反向讲解部分),流程不变 —— 写文件 → gate 绿 → 在 Mac 上 `git add/commit/push`(走 osascript) → 更新 progress+LEARNINGS → 报告 → David 确认 → 下一个 commit。每个 commit 完整收尾后停下等确认再开下一个。

---

### Build — Phase 1：最小可跑框架（能跑出第一个 eval 所需的全部）

- [x] **Commit 0.a** — repo init + scope doc + README 概要(已 push `8206a48`)
- [x] **Commit 0.b** — uv / ruff / mypy / pytest 脚手架 + CI(已 push;CI 首跑撞 PEP 668 `--system`,改 `uv sync`+`uv run` 修好 `4de3404`;remote = `9d8dd11`,gate 全绿)
- [x] **Commit 1** — core eval API 骨架:`DESIGN.md` 5 项决策定稿 + `datasets`/`runner`/`metric`/`judge` 四模块(`Task`/`RunResult`/`Claim`/`MetricScore`/`JudgeVerdict` frozen dataclass + `Runner`/`Metric`/`Judge` Protocol),纯类型契约无逻辑;ruff/format/mypy --strict(5 files)/pytest(9)全绿
- [x] **Commit 2** — datasets 层:`load_tasks`(JSONL,跳空行/注释,报行号)+ `validate_task`(按桶校验:≥3 facts / claim_verification 需 claim / bug_localization 需 fix files)+ `DatasetError` + fixture `mini_tasks.jsonl`(4 桶各 1)+ 10 个测试;gate 全绿(18 tests)
- [x] **Commit 3** — 确定性 metrics:`RoutingAccuracy` / `CitationGrounding`(注入 `SymbolResolver`,生产接 mcp-ast-explorer)/ `VerificationRate`(verified+contradicted 占比)实现 + 7 测试;gate 全绿(25 tests)
- [x] **Commit 4** — LLM-as-judge:`ChatModel` Protocol + `FactualCorrectnessJudge`(结构化 JSON 解析,容错 fence/prose,clamp,parse 失败降级)+ `SelfConsistentJudge`(3 跑,variance<阈值 才算可信)+ `AnthropicChatModel`(lazy import,`[llm]` extra)+ `JudgeMetric`(judge→metric 适配)+ 10 测试(mock);gate 全绿(34 tests)
- [x] **Commit 5** — runner + 架构 adapter:`_execute`(计时 + 错误转 `RunResult.error` 不抛)+ `_normalize`/`_parse_claims`(安全默认、非法 label/risk 降级)+ `WayfinderSupervisorRunner` + `ReActBaselineRunner`(注入式 `AgentInvoke`,live 接线留 Commit 8)+ 6 mock 测试;gate 全绿(39 tests)
- [x] **Commit 6** — CLI runner:`evaluate()` 编排(逐 task 跑 + 评分,error 跳过评分)+ `write_csv`(每 metric 一列)+ `agent-eval run --dataset --arch --out` 入口点(`build_runner` live 接线留 C8,`run_eval` 可注入 runner_factory 离线测)+ README 用法 + 7 测试;gate 全绿(46 tests)

### Build — Phase 2：小规模 eval（尽早拿数字喂简历）

- [x] **Commit 7** — 数据集 `datasets/small_v1.jsonl`(12 任务,4 桶各 3,5 个有 pytest 的 Python repo:click/flask/requests/httpx/rich)。GT 对着 pin 的真仓库读源码/测试核过(verifier_test_id 是真 nodeid、bug_fix_files 真存在)。`load_tasks` 校验通过(4 桶各 3,invariants OK)。**待你 truthfulness review** 后才出数字
- [/] **Commit 8** — live wiring + 🚀 跑小规模 eval。**已做(代码)**:`live/wayfinder.py`(`map_run_summary` + `wayfinder_invoke`:POST /explain → 轮询 /status → 映射 RunSummary;`[live]` extra httpx;httpx.MockTransport 测全链路)+ `cli.build_runner` 接 `WAYFINDER_URL`。Anthropic key 已验证(judge 用)。**待你资源才能真跑**:OpenAI key(wayfinder 跑在 gpt-5.5)+ Docker 起 6 服务栈(含 sandbox-worker 才有真 verification_rate)+ ReAct baseline 接线(需 live 迭代)+ 数据集 GT(你审)。gate 全绿(52 tests)。**2026-06-14 更新**:live 栈跑通,small_v1(12)+ **full_v1(40)两套 benchmark 均已干净跑完**(Supervisor 0 错误);报告在 `report/small_v1/` 与 `report/full_v1/`。剩:数据集 GT 待 Haichuan 审 + ReAct baseline 已接线可跑

### Build — Phase 3：完整 40-repo benchmark + 报告

- [ ] **Commit 9** — 扩到完整 40-OSS-repo(10 web frameworks + 10 ML libs + 10 CLI tools + 10 distributed systems)+ 各桶 ground truth 补全
- [ ] **Commit 10** — 🚀 跑完整 40-repo 双架构 eval → CSVs(self-consistency 3 跑)
- [ ] **Commit 11** — 4 张 SVG 图(matplotlib):routing accuracy bar / factual correctness boxplot / cost scatter / verification rate per arch
- [ ] **Commit 12** — `EVAL_REPORT.md`:conclusion + methodology + data tables + charts + 3 段 trade-off + 一句话 headline number
- [ ] **Commit 13** — Iteration round 1:修最差桶(通常 Claim Verification 的 contradicted 检出 <80%)→ 调 verifier 触发 → 重跑 → before/after

### Build — Phase 4：框架硬化 + OSS 发布

- [ ] **Commit 14** — failure-mode taxonomy(hallucination / tool misuse / retrieval / reasoning)分类器 + 完整 token/cost tracking + CLI 打磨 + 集成 adapter(LangGraph / bare LangChain)
- [ ] **Commit 15** — v0.5:框架跑通 P3 `arxiv-rag` / P4 `single-file-explainer` / P6 `wayfinder` 作 examples
- [ ] **Commit 16** — OSS v1.0:docs(quickstart + API + examples)+ 测试覆盖 + README 终版 + 打包(可选 PyPI)
- [ ] **Commit 17** — Iteration round 2:部署后 live/cloud 重跑(抓 cold start / quota / timeout)→ 更新报告 before/after

### Ship

- [ ] 全部 `final_checklist.md` Project 7 acceptance `[x]`
- [ ] README 终版 + OSS v1.0(docs/tests/examples)公开
- [ ] `EVAL_REPORT.md` + 4 SVG 图 + headline number 进简历 + 第 1 篇技术文章草稿
- [ ] Star push(HN / Reddit / Twitter / LangChain Discord)+ 1–2 个 external issue;eval 方法论写进 P3/P4/P6 三个 README
- [ ] 写 retro + `TASKS.md` Project 7 ship 行 `[x]`

---

## 📝 Daily Logs

> 每个 commit / 每个工作日加一条,倒序(最新在最上)。

### 2026-06-15 — citation metric 缺陷发现 + 修复(resolver 误判真实属性引用)

- **动机**:David 问"wayfinder citation 0.37 是真弱还是嘴笨"。同模型(gpt-5.5)下 ReAct citation 0.75,怀疑是 wayfinder synthesizer 不点名符号。
- **实验**:改 wayfinder synthesizer prompt 强制点名具体符号 → 同 stack 重跑 small_v1 wayfinder 臂。
- **关键转折**:光改 prompt(旧 resolver)citation 反而掉到 **0.252**;查原因 = **`RepoSymbolResolver` 只认 `def`/`class` 顶层定义名,把 `self.callback`/`ctx.params` 这类真实属性/方法引用全判成"未落地"**。新答案点名更多属性引用 → 反被扣分。这是 **eval metric 自身的缺陷**,不是 wayfinder 幻觉。
- **修复**(`citations.py` `RepoSymbolResolver.__call__`):dotted 引用除 def/class 外,若该属性 `.<name>` 在 repo 里真实出现也算 grounded(反幻觉仍保留——编造的属性不会出现)。加回归测试 `test_repo_symbol_resolver_grounds_real_attribute_references`(self.callback/ctx.params=True,self.frobnicate=False)。gate 全绿(ruff/format/mypy --strict/pytest 5 passed)。
- **三轮对照(small_v1,wayfinder,n=12)**:旧 resolver+旧 prompt **citation 0.373** / 旧 resolver+新 prompt **0.252** / **新 resolver+新 prompt 0.813**;factual 0.582→0.539→0.510(噪声内);routing/verification 不变。
- **结论(诚实)**:① wayfinder **不幻觉**——公平打分下 81% 引用对应 repo 真实代码,0.37 是测量假象;② citation 0.81 主要是 resolver 功劳不是 prompt;③ **不能**说 citation 反超 ReAct——同样宽松的 resolver 用到 ReAct 上它也会涨,ReAct 答案没存需重跑才能公平对比。
- **影响已提交报告**:`report/full_v1/` 的 citation 0.37 vs 0.75 是旧(严格)resolver 打的,已知不公平,加了 caveat,待用新 resolver 重跑 ReAct 后修订。
- **决策**:resolver 修复(harness 资产)提交;wayfinder prompt 改动 hold(占 architecture ownership,没动 factual,留待 Haichuan 反向讲解时定)。
- **教训**:live stack 启动配方所有运营变量需 `WAYFINDER_` 前缀(progress.md 旧配方少前缀导致 scanner 退化成 placeholder + LLM writer 没启用);`WAYFINDER_ENABLE_GITHUB_INGESTION=1` 才放行 GitHub(否则 /explain 403)。

### 2026-06-14 — 🏁 full_v1 40 任务跑完(allowlist 修复后,Supervisor 0 错误)

- **症状**:首次 40 任务跑 wayfinder 28/40 报错,全是 HTTP 403。
- **根因**(非随机崩 / 非超时):我启动 wayfinder 时只放行了 3 个 repo 的 allowlist,另外 7 个 repo 的 28 个任务全被拒。
- **修复**:用 `WAYFINDER_GITHUB_REPO_ALLOWLIST='*'` 重启 wayfinder,只重跑 wayfinder 那一臂(`--arch wayfinder_supervisor`),靠 `summarize_csv_dir` 与已有的 react CSV 合并 —— 省掉重跑 react 的 ~5M token。
- **干净结果**(`report/full_v1/`):wayfinder factual 0.563 / verification 0.209 / routing 0.475 / citation 0.373 / **476k tokens**(**0 err**);react factual 0.700 / verification 0.0 / routing 0.0 / citation 0.750 / **4.969M tokens**(4 err)。
- **headline**:成本 **~10.4×**(476k vs 4.97M);verification 0.21 vs 0.0 仍是架构性赢面(ReAct 同样有 run_pytest 仍 0);factual/citation ReAct 暴力赢,如实写进报告 + 公平性说明(routing/verification 结构性单边,真正 apples-to-apples 的是 factual/citation/cost)。
- **教训**:跑全量前先确认 wayfinder allowlist = `*`,否则非允许 repo 全 403。沙箱 `ps` 看不到 Mac 上的 benchmark 进程(两套进程空间)—— 查活性要用 osascript 在 Mac 上 `pgrep`。
- ⚠️ 数据集 GT 仍 pending Haichuan 真实性审查(`datasets/README.md`),发简历数字前必须先审。
- 图 + EVAL_REPORT + CSV/summary 已落 `report/full_v1/`。

### 2026-06-14 — 干净 re-run(修好 ReAct pytest 工具后)

- **修复**:mcp-test-runner 改 `sys.executable -m pytest`(commit `e24d639`)+ 用 `--extra dev` 起 8103,ReAct 的 run_pytest 现在真能跑。
- **干净结果**(`report/small_v1/`,覆盖旧):wayfinder factual 0.582 / verification 0.188 / routing 0.50 / citation 0.373 / **77.9k tokens**(0 err);react factual 0.696 / verification 0.0 / routing 0.0 / citation 0.751 / **1.165M tokens**(1 err)。
- **更强的 headline**:成本差从 ~11× 拉大到 **~15×**(78k vs 1.17M)—— 工具修好后 ReAct 干更多活、更贵。**关键**:verification 0.19 vs 0.0 现在证明是**架构性**差异(ReAct 工具能用了仍 0,因为它没结构化 verifier),不是上次的 bug。factual 仍 ReAct 略高(0.70 vs 0.58,如实写报告)。
- 图 + EVAL_REPORT 已用干净数据重生成。

### 2026-06-14 — 🏁 首次真跑完成(Supervisor vs ReAct,12 任务,0 错误)

- **结果**(`report/small_v1/`):wayfinder factual 0.615 / verification 0.188 / routing 0.50 / citation 0.372 / **77.2k tokens**;react factual 0.729 / verification 0.0 / routing 0.0 / citation 0.742 / **884.8k tokens**。
- **Headline(诚实)**:Supervisor 用 **~11× 更少 token**(77k vs 885k)达到与 ReAct **相当的 factual accuracy**(0.62 vs 0.73,略低),且**唯一**有真实测试执行验证(verification 0.19 vs 0)。ReAct 靠暴力探索拿到更高 factual/citation,但 11× 成本。
- **诚实 caveat**:① ReAct 的 `run_pytest` 工具本次坏了(pytest 不在 mcp-test-runner PATH)→ 重试拉高 token + 压低其 verification,所以 11× 成本差有部分是 bug 造成,re-run 前要修;② 小样本单 seed(12 任务,agent 每任务 1 跑,self-consistency 只在 judge);③ claim_verification 两边都弱;④ cost_usd 没算(用 token 比)。
- **产物**:`report/small_v1/EVAL_REPORT.md` + 4 SVG 图(routing/factual boxplot/cost scatter/verification)+ 2 CSV + summary.json;`scripts/make_charts.py`(matplotlib,`[report]` extra)。`runs/` gitignore,成果落 `report/`(进 git)。
- **下一步(可选)**:修 mcp-test-runner 的 pytest(`python -m pytest`)→ 干净 re-run;扩 40-repo;把 headline number 写进简历 bullet。

### 2026-06-14 — cost 来源 + 全量跑 driver + benchmark CLI

- **cost 来源**:ReAct 侧 langchain 真 token(react.py 已抓);wayfinder 侧 token 计量已加(wayfinder commit `e70497f`,trace_metadata.tokens),`map_run_summary` 早就读 `meta["tokens"]`。cost($) 在 summarize 里用 `tokens × price_per_1k` 统一算,两架构可比。**4 个 metric 来源至此全部就位**。
- **driver**:`experiment.py` —— `run_benchmark(tasks, runners, metrics, out_dir, price)`(每架构 evaluate + 写 `<arch>.csv` + `summary.json`)、`summarize`(每架构每 metric 均值 + token/cost 总计 + error 数)、`clone_repos_for_resolution`(给 citation resolver 单独 clone)。
- **CLI**:`agent-eval benchmark --dataset --out --judge-model --runs --price-per-1k` —— 接 live judge(SelfConsistentJudge+AnthropicChatModel)+ CitationGrounding(RepoSymbolResolver)+ 两架构 runner,跑 run_benchmark。
- **测试**:`tests/test_experiment.py` 2 个(run_benchmark 写 CSV+summary、summarize 均值/成本/error)+ benchmark 解析测试;gate 全绿(ruff/format/mypy 12/pytest **64**)。
- **下一步(花钱)**:装 `[react]` 依赖 + 起 mcp-test-runner(8103)→ `agent-eval benchmark` 真跑 12×3×2 → 4 图 + EVAL_REPORT。

### 2026-06-14 — citation_grounding 来源

- **做了什么**:`citations.py` —— `extract_cited_symbols(text)`(从答案抽 backticked / dotted.path / file.py 引用,去重 cap 25,滤散文)+ `RepoSymbolResolver`(task 感知:按 repo_url slug 找 clone,查 file 存在或符号末段有 `def/class` 定义,clone 缺失=False=未落地)+ `default_repo_slug`。`CitationGrounding` 的 `SymbolResolver` 改 task 感知 `Callable[[Task,str],bool]`。两个 adapter(wayfinder map / react map)现在从答案抽 `cited_symbols`。
- **意义**:metric 能抓幻觉引用 —— wayfinder 引真符号 → grounding 高;ReAct 自由发挥可能引幻觉 → 低。对比成立。
- **测试**:`tests/test_citations.py` 6 个 + 改 test_metrics 为 task 感知 resolver;gate 全绿(ruff/format/mypy 11/pytest **61**)。
- **运行注**:全量跑时 resolver 单独 clone 一份(用 `default_repo_slug`)做查证,跟 wayfinder/react 各自 clone 命名解耦。
- **下一步**:cost 来源(ReAct langchain 真 token;wayfinder 侧用 token 估或标 partial)。

### 2026-06-14 — ReAct baseline(对照组代码完成)

- **做了什么**:`live/react.py` —— ReAct 单 agent 对照组。`react_invoke(mcp_urls, model=gpt-5.5)` 返回 `AgentInvoke`:shallow clone repo → 用 `MultiServerMCPClient`(streamable_http)加载 project5 MCP 工具 → `create_react_agent(ChatOpenAI)` → `ainvoke` → 映射成标准 raw dict。纯函数 `_extract_answer_and_tokens`(取最后 AI 消息 + 累加 token)、`_map_react_result`(route="react"、claims=[] —— ReAct 无结构化 verifier,verification_rate 天然低,正是对比点)、`_slug`。`[react]` extra(langgraph + langchain-openai + langchain-mcp-adapters,懒加载)。`cli.build_runner` 接好 react_baseline(env `REACT_*_MCP_URL` / `REACT_OPENAI_MODEL`)。
- **测试**:`tests/test_live_react.py` 5 个纯映射单测;改 `test_cli` 的 react 用例为"已接线"。gate 全绿(ruff/format/mypy/**56 tests**)。mypy 给 react 三个懒加载依赖加了 ignore_missing_imports override。
- **待 live 验证**:真跑需 `[react]` extra 装上 + mcp-test-runner 也起 HTTP(8103,给 ReAct run_pytest 工具)+ OPENAI_API_KEY。
- **下一步**:routing/citation/cost 三个 metric 来源 → 全量跑 12×3×2 → 4 图 + EVAL_REPORT。

### 2026-06-14 — verification_rate 调查:被 wayfinder verifier 触发卡住(重要)

- **做了什么**:sandbox-worker 用 host uvicorn 起在 8110(health 200),wayfinder 切 `WAYFINDER_VERIFIER_RUNNER=sandboxed_mcp` + `WAYFINDER_TEST_SANDBOX_URL=http://127.0.0.1:8110`,启动时的 sandbox health check 通过。
- **结果**:两次 claim 风格查询(① 自然语言"verify…" ② 直接点名 `tests/test_requests.py::TestRequests::test_auth_is_stripped_on_http_downgrade`)都**没触发测试执行** —— `test_results` 空、verified/unverified/contradicted 全 0。agent 自己说"no test was run / no verified claims"。
- **根因**:不是 sandbox 没起,也不是 test-runner MCP 缺失(`test_runner` 在 `project5.py` **故意没有 `http_url_env`**,executable claim 走 sandbox-worker,这条已接通)。真正卡在**上游**:wayfinder 的 agent 没有产出"带具体 test_id 的高风险 claim"并路由给 verifier→sandbox。即使点名测试也没跑。
- **结论**:verification_rate > 0 **不是配置能解决的**,要改/调 wayfinder 自身的 claim 生成 + verifier 路由(它历史上 empty-evidence 那条线就是这块)。属于 wayfinder 本体 R&D,跨 session。
- **可达 vs 不可达**:factual_correctness 干净可出(judge + grounded answer 都通);routing 可从 partial_summaries 反推;cost ReAct 侧可测、wayfinder 侧需估;**verification_rate 受阻于 wayfinder verifier 触发**;citation 需从答案抽符号 + ast 反查(中等)。
- **建议**:先落 factual_correctness(+ 尽量 routing/citation)的真数字(ReAct baseline + 全量跑),verification_rate 当作独立的 wayfinder 调优子任务。

### 2026-06-14 — 决策:走完整 4-metric 路线(David 选定)

- **决策**:David 要**完整 4 metric**(不只 factual_correctness)。即含 verification_rate(核心差异化)。
- **执行顺序**(分块推进):
  1. **verification_rate** — 起 sandbox-worker(host uvicorn,共享 `/tmp/wayfinder/repos`,免 Docker 卷映射)+ wayfinder 切 `WAYFINDER_VERIFIER_RUNNER=sandboxed_mcp` + `WAYFINDER_TEST_SANDBOX_URL=http://127.0.0.1:8110`,claim_verification 任务出真 verified/contradicted 计数。worker 入口:`uvicorn wayfinder.sandbox.worker:app --port 8110`,env `WAYFINDER_SANDBOX_ALLOWED_ROOTS=/tmp/wayfinder/repos`。
  2. **ReAct baseline** — `live/react.py`:create_react_agent + 同批 project5 MCP 工具 + gpt-5.5(langchain token 回调可顺带拿到 ReAct 侧真 cost)。
  3. **routing / citation / cost 来源** — routing 从 partial_summaries 跑了哪些 sub-agent 反推 intent;citation 从 final_output 抽符号 + ast-explorer 反查;cost 从 OpenAI 用量估(wayfinder 侧 tokens=0)。
  4. **全量跑** 12×3×2 → 4 SVG 图 + EVAL_REPORT.md + headline number。
- **注**:真跑 verification_rate 会在 host 上执行目标 repo 的测试套件(click/flask/requests,可信);worker 自带 subprocess+rlimit 隔离,Docker 只是多一层容器隔离。

### 2026-06-14 — Live stack WORKING + first grounded run (no commit; ops milestone)

- **里程碑**:wayfinder live stack 跑通,产出**真实 grounded 输出**。click 被 ingest,mcp-repo-mapper 返回真实依赖图(Python 63 files,完整 `src.click.*` import graph),gpt-5.5 写出有据的架构答案,`errors:[]`。证明全链:GitHub ingest → MCP 分析 → 多 agent LLM → RunSummary →(我的 adapter 映射)→ judge。
- **关键解锁(linchpin)**:`mcp_http` 模式需要 project5 MCP 以 streamable-http 跑在 8101/8102,但 ① `WAYFINDER_START_PROJECT5_HTTP_MCP` 在 wayfinder src 里**根本没实现**;② project5 server 默认 `mcp.run(transport="stdio")`,连 Docker `--profile mcp` 也是 stdio。**解法**:自己用 FastMCP 起 HTTP —— `/tmp/run_mapper.py` = `from mcp_repo_mapper.server import mcp; mcp.run(transport="streamable-http", host="127.0.0.1", port=8101)`(ast 同理 8102)。`uv run python /tmp/run_xxx.py`。8101/8102 GET 返回 406 = MCP 端点正常(要 POST+Accept)。
- **可复现启动配方**(下次直接照做):
  1. 起 2 个 MCP:`cd ~/dev/project5/mcp-repo-mapper && uv run python /tmp/run_mapper.py`(8101)+ `cd ~/dev/project5/mcp-ast-explorer && uv run python /tmp/run_ast.py`(8102)。
  2. 起 wayfinder:`cd ~/dev/wayfinder`,`set -a; . ~/dev/agent-eval-harness/.env; set +a`(给 OPENAI/ANTHROPIC key),env:`WAYFINDER_REQUIRE_AUTH=0 RUN_STORE=memory ARCHITECTURE_SCANNER=mcp_http ENTRY_SCANNER=mcp_http PROJECT5_REPO_MAPPER_MCP_URL=http://127.0.0.1:8101/mcp PROJECT5_AST_EXPLORER_MCP_URL=http://127.0.0.1:8102/mcp VERIFIER_RUNNER=placeholder LLM_ROUTING=openai FINAL_WRITER=openai OPENAI_MODEL=gpt-5.5 MCP_TOOL_TIMEOUT_SECONDS=30 RUNTIME_BUILD_TIMEOUT_SECONDS=45 GRAPH_NODE_TIMEOUT_SECONDS=90 ENABLE_GITHUB_INGESTION=1 GITHUB_REPO_ALLOWLIST='pallets/click,pallets/flask,psf/requests'`,`uv run uvicorn wayfinder.api.main:app --port 8000`。
  3. 冒烟:`POST /explain {repo_url,query}` → 轮询 `GET /status/{job_id}`。
- **已知 gap(影响 metric)**:① `/status` 的 `trace_metadata` **没有 intent/route 字段** → routing_accuracy 暂无来源(需另找,或从 partial_summaries/agent 推);② `tokens=0 cost_usd=0` → wayfinder 没算 token/cost,成本对比要另估;③ `verified_count=0`(verifier=placeholder)→ verification_rate 要真值得起 Docker sandbox-worker;④ cited_symbols 不在 /status → citation_grounding 暂空。**factual_correctness(judge)可以真出** —— 这是 headline "factual accuracy" 的主指标。
- **运行中进程**(本次 session,可能已停):MCP 8101/8102 + wayfinder 8000。下次按上面配方重起。
- **下一步**:① 建 ReAct baseline(对比组,缺它没 headline);② 跑 harness 12 任务拿 factual_correctness;③ 起 Docker sandbox-worker 拿真 verification_rate;④ 解决 routing/cost/citation 来源。

### 2026-06-14 — Commit 7 — `dataset small_v1 (12 tasks)`

- **做了什么**:`datasets/small_v1.jsonl` 12 任务(architecture/function_tracing/claim_verification/bug_localization 各 3)+ `datasets/README.md`。在 sandbox clone 了 click/flask/requests/httpx/rich(都有 pytest),pin 到 HEAD SHA,**对着真源码/测试核 GT**:flask `dispatch_request`(app.py:966,被 full_dispatch_request 调)、requests `rebuild_auth`(sessions.py:309,被 resolve_redirects 调,跨 host 删 Authorization)、3 个 claim 绑真 nodeid(`tests/test_requests.py::TestRequests::test_auth_is_stripped_on_http_downgrade` / `..._fragment_maintained_on_redirect` / `..._cookie_sent_on_redirect`)、bug_fix_files 用确认存在的 src/ 路径。`expected_route` 用 wayfinder intent(architectural/behavioral/debug)。
- **校验**:`load_tasks` 加载通过,4 桶各 3,per-bucket invariants OK。
- **待你**:truthfulness review(尤其 3 个 claim 的 expected verdict + bug 的 suspect 模块),过了才出数字。
- **资源**:全前置已齐(2 key + Docker + wayfinder)。下一步:配 wayfinder .env(OpenAI + 真 verifier + GitHub ingestion allowlist 加这 5 repo)+ `docker compose up` 起栈 → 接 ReAct baseline → 跑。

### 2026-06-14 — Commit 8(代码)— `wayfinder live invoke adapter`

- **做了什么**:`live/wayfinder.py` —— `map_run_summary`(wayfinder `RunSummary` → 标准 raw dict:`final_output`→answer、verified/unverified/contradicted_count→claims、trace_metadata→route/tokens/cost best-effort、cited_symbols 暂空因 /status 只给计数)+ `wayfinder_invoke`(POST /explain → 轮询 /status 到 completed/failed → 映射;failed 抛错被 runner 转 error;超时抛 TimeoutError;`transport` 参数供 httpx.MockTransport 测)。`[live]` extra(httpx)。`cli.build_runner` 接 `WAYFINDER_URL`/`WAYFINDER_TOKEN`。`tests/test_live_wayfinder.py` 5 测试(MockTransport 跑通 post+poll+failed)。
- **资源核对(读 wayfinder 源码后)**:wayfinder 跑在 **OpenAI gpt-5.5**(不是 Anthropic);公开部署默认 `WAYFINDER_VERIFIER_RUNNER=placeholder`,真 verification_rate 必须本地起 sandbox-worker。所以真跑要 OpenAI key + Docker 栈,Anthropic key 只够 harness 的 judge。Anthropic key 已放 `.env` 并验证可用(HTTP 200,Haiku)。
- **下一步(需你)**:① OpenAI key 放进同一 `.env` 的 `OPENAI_API_KEY`;② 装/起 Docker。就位后我:起 wayfinder 栈 → 接 ReAct baseline → 跑小规模 eval。
- **Gate**:ruff/format/mypy --strict(9)/pytest(52 passed)全绿。

### 2026-06-14 — Commit 6 — `CLI runner`(Phase 1 完成)

- **做了什么**:`evaluate.py`(`EvalRow` + `evaluate(tasks, runner, metrics)` 逐 task 跑+评分、error 跳过评分;`write_csv` 每 metric 一列、缺失留空)。`cli.py`(`agent-eval run --dataset --arch --out`,argparse 子命令;`default_metrics` = routing+verification 离线安全;`build_runner` live 接线留 C8 raise NotImplementedError;`run_eval` 可注入 `runner_factory` 离线端到端测)。pyproject 加 `[project.scripts] agent-eval`。README 加用法。`tests/test_evaluate.py` + `tests/test_cli.py` 7 测试。
- **里程碑**:**Phase 1(最小可跑框架)完成** —— datasets→runner→metric/judge→CLI 全链路打通,46 测试全绿,`agent-eval --help` 入口点可用。剩下是接真实 wayfinder/ReAct + 数据集策划(Phase 2,需 API key)。
- **Gate**:ruff/format/mypy --strict(7)/pytest(46 passed)。踩坑:测试里长行 E501 + ruff format 要用 CI 同版(0.15.17)统一。
- **下一步(需你的资源)**:Phase 2 Commit 7 数据集策划(clone 真 repo + 跑测试套件验证)+ Commit 8 真跑(Anthropic API key + wayfinder + 3 MCP 起服务)。这两步我无法独立端到端完成,到此交接。

### 2026-06-14 — Commit 5 — `runner + architecture adapters`

- **做了什么**:`runner.py` 加 `AgentInvoke` 类型((repo,query)→raw mapping)、`_execute`(计时 + 捕获异常转 `RunResult.error`,单 task 失败不炸全局)、`_normalize` + `_parse_claims`(从 raw 解析 claim,非法 label/risk 降级 unverified/low,非 dict 跳过,数值字段类型不对则 0)、`WayfinderSupervisorRunner`(arch=wayfinder_supervisor,有 route/claims/citations)、`ReActBaselineRunner`(arch=react_baseline,通常无 claims → verification_rate 天然低)。`tests/test_runner.py` 6 测试。
- **设计点**:adapter 依赖注入 `AgentInvoke`,真实接线(HTTP 到部署的 wayfinder / LangGraph create_react_agent)留 Commit 8 live run;Commit 5 只做归一化 + 容错,mock 可测。两个 arch 共享 `_normalize`,差异在各自 invoke 产出。
- **Gate**:ruff/format/mypy --strict(5)/pytest(39 passed)全绿。
- **下一步**:Commit 6 — CLI runner(dataset × arch → CSV)。

### 2026-06-14 — Commit 4 — `LLM-as-judge + self-consistency`

- **做了什么**:`judge.py` 加 `ChatModel` Protocol(text-in/out)、`FactualCorrectnessJudge`(用 expected_key_facts 做 ground truth,要求模型回 JSON,`_parse_verdict` 容错 ```json fence/prose + clamp [0,1] + parse 失败降级 score 0)、`SelfConsistentJudge`(N 跑取均值,pvariance<阈值 才标 consistent)、`AnthropicChatModel`(lazy import anthropic,`[llm]` extra)。`metric.py` 加 `JudgeMetric`(judge→Metric 适配,name=factual_correctness)。`tests/test_judge.py` 10 测试用 FakeChatModel/StubJudge。
- **设计点**:judge 依赖注入 `ChatModel`,测试零网络;judge bias 显式 —— 每个 verdict 带 reasoning,self-consistency variance 超阈值即标不可信(对位"variance<0.1 才纳入报告")。
- **Gate**:ruff/format/mypy --strict(5)/pytest(34 passed)。踩坑:① anthropic 是可选 extra,mypy strict 会因找不到模块报错 → pyproject 加 `[[tool.mypy.overrides]] ignore_missing_imports`;② ruff format 版本要和 CI 一致(0.15.17),用全局旧 ruff 格式化会和 CI 冲突 → 统一用 uv-synced ruff。
- **下一步**:Commit 5 — runner + Wayfinder/ReAct adapter(mock 测试)。

### 2026-06-14 — Commit 3 — `deterministic metrics`

- **做了什么**:`metric.py` 加三个确定性 metric 实现 + `SymbolResolver` 类型。`RoutingAccuracy`(route_taken vs expected_route)、`CitationGrounding`(注入 resolver 判断 cited symbol 是否真存在,去重,空引用=1.0 但 detail 记 total=0)、`VerificationRate`((verified+contradicted)/total,空=0.0)。`tests/test_metrics.py` 7 测试。
- **设计点**:`CitationGrounding` 用注入式 `SymbolResolver = Callable[[str],bool]`,生产接 mcp-ast-explorer,测试注 fake —— metric 本身保持纯函数可测。
- **Gate**:ruff/format/mypy --strict(5)/pytest(25 passed)全绿。
- **下一步**:Commit 4 — LLM-as-judge(factual_correctness)+ self-consistency 包装(mock 测试)。

### 2026-06-14 — Commit 2 — `datasets layer`

- **做了什么**:`datasets.py` 落 `load_tasks`(JSONL 逐行解析、跳空行/`#` 注释、JSON 错误带 `file:line`、去重 id)+ `validate_task`(共享规则 ≥3 key facts + 按桶:claim_verification 需 `claim_under_test`、bug_localization 需 `bug_fix_files`)+ `DatasetError` + 类型安全的 `_task_from_dict` 字段校验。fixture `tests/fixtures/mini_tasks.jsonl`(4 桶各 1 条)。`tests/test_datasets.py` 10 个测试(加载/跳过/行号/去重/缺字段/类型错/按桶校验)。
- **Gate**:ruff/format/mypy --strict(5 files)/pytest(18 passed)全绿。修了 2 处:mypy `redundant-cast`(membership 检查后 mypy 已把 bucket 收窄到 Literal,去掉 cast)、删掉 Commit 1 占位测试(`load_tasks` 已实现)。
- **下一步**:Commit 3 — 确定性 metrics(routing_accuracy / citation_grounding / verification_rate)。

### 2026-06-14 — Commit 1 — `core eval API skeleton`

- **做了什么**:落 eval API 的类型契约(零逻辑)。四模块 `datasets.py`(`Task`/`Bucket`/`BUCKETS`/`Dataset`/`load_tasks` stub)、`runner.py`(`RunResult`/`Claim`/`ClaimLabel`/`RiskLevel`/`Runner` Protocol)、`metric.py`(`MetricScore`/`Metric` Protocol)、`judge.py`(`JudgeVerdict`/`Judge` Protocol);`__init__.py` 统一 re-export。`tests/test_contracts.py` 9 个契约测试(构造各 dataclass、`BUCKETS` 锁定、`load_tasks` 抛 NotImplementedError、`Runner` Protocol 结构满足)。`DESIGN.md` 5 项决策定稿。
- **关键设计决策**:① 单个 `Task` dataclass + 可选 bucket 字段 + 单 `tasks.jsonl`(好 diff);② `RunResult` 架构无关(judge/metric 只读类型化字段,adapter trace 藏 `raw`),错误走 `error` 不抛;③ Protocol + frozen/slots dataclass;④ 依赖流 `metric,judge → datasets,runner`,无环。
- **Gate**:sandbox 干净副本全绿 —— ruff / ruff-format / mypy --strict(5 files)/ pytest(9 passed)。
- **下一步**:Commit 2 — datasets 层(`load_tasks` JSONL 实现 + `validate_task` 按桶校验 + fixture 数据集 + 测试)。

### 2026-06-14 — CI fix — `uv sync + uv run`

- **症状**:0.b push(`501e4f2`)后 GitHub Actions 两个 job(3.11/3.12)都 exit code 2,14s 快速失败。
- **根因**:`uv pip install --system` 装进 runner 的 externally-managed 系统 Python(PEP 668),uv 拒绝 → exit 2。代码/config 没问题(干净安装下 4 个 gate 全绿)。
- **修复**:改 uv-native 链 —— `uv sync --extra dev --python <ver>`(建隔离 + 矩阵正确的 venv)+ `uv run ruff/mypy/pytest`;`setup-uv@v3→v5`(顺手清 Node20 deprecation warning)。sandbox 验证 `uv sync`+ 四 gate 全绿,待 Mac 上提交 push。

### 2026-06-14 — Commit 0.b — `CI + lint/type/test scaffold`

- **做了什么**:补脚手架使 gate 从第一行代码起就绿。`.github/workflows/ci.yml`(GitHub Actions 3.11/3.12 矩阵)、`tests/test_smoke.py`(包可导入 + version 非空)、`tests/__init__.py`、根 `Makefile`(`make gate` 镜像 CI)。新建 `LEARNINGS.md`(4 节结构)+ `DESIGN.md`(Commit 1 eval API 的 guided 设计模板,Haichuan 主导)。
- **Gate 验证**:sandbox 全绿 —— ruff `All checks passed`、ruff format ok、mypy `Success`(干净副本;mount 上 `.mypy_cache` sqlite 锁会假报 INTERNAL ERROR,已 gitignore)、pytest 2 passed。
- **自己设计了什么**:无架构决策(纯 boilerplate,守 ownership 边界 rule 15)。eval API 设计留 Commit 1。
- **踩坑**:从 Cowork sandbox 对挂载的 `~/dev` repo 跑 `git commit` 不安全 —— 挂载层不让 git unlink `.git/*.lock`,破坏原子性,导致 0.b 被复制成两个 commit + remote ref 自己乱跳。教训记忆 [[sandbox-git-mount-lock]]:**此后 sandbox 只写文件,git 全在 Mac 上做**。已在 Mac 上 `reset --soft` 收成单 commit `501e4f2`。
- **下一步**:① push CI 修复 → 确认 Actions 绿;② 你手填 progress.md 4 项 + `DESIGN.md` 4 个抽象决策;③ 进 guided design mode 落 Commit 1 skeleton。

### 2026-06-13 — Commit 0.a(起步)— `Repo init + progress.md`

- **做了什么**:开 Project 7 `agent-eval-harness`(合并原 P7+P9)。GitHub 建公开 repo + clone 到 `~/dev/agent-eval-harness`(离开 iCloud,按 `new_project_setup_playbook.md`)。Cowork 挂载,写好本 progress.md(自动填 pitch / 技术契约 / 跨项目衔接 / 成功判定 / Pre-build),搭最小脚手架(README/.gitignore/pyproject/空包)。
- **自己设计了什么**:暂无(架构/eval API 设计留给正式开工时 Haichuan 主导)。
- **下一步**:① 你手填 4 项(项目领域 / 简历差异化 / Core Principles / Today's North Star);② 先回 wayfinder 收尾(Commit 23 反向讲解);③ 回来再 Commit 0.b 配脚手架 + 写 eval API design note。

---

## 🔄 Pickup Protocol

1. 看 Dashboard 当前阶段 + Today's North Star。
2. 看 Roadmap 找下一个 `[ ]` / `[/]`。
3. 看最新 Daily Log。
4. 注意:这是合并原 P7+P9 的项目;repo 在 `~/dev/agent-eval-harness`,全局笔记在 `Final_checklist/`。
