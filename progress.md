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
| 当前阶段               | **Building — Phase 1 完成**(最小可跑框架 C1–C6 全绿);下一步 = Phase 2 数据集策划/真跑(需 API key + wayfinder) |
| 进度                   | 0 / N acceptance criteria done(脚手架不计 acceptance）     |
| 完成 commits           | 0.a · 0.b · CI fix · C1–C5 · **C6 CLI runner**(Phase 1 最小框架完成) |
| Gate 状态              | ✅ ruff / ruff-format / mypy --strict(7 files)/ pytest(46 passed);CI uv-native(`uv sync`+`uv run`) |
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

- [ ] **Commit 7** — 策划 10–15 repo 数据集(4 桶,每个 repo ≥1 可跑 pytest/jest,smoke 筛掉破损套件)+ 标注 ground truth(query / ≥3 key facts / expected route / verifier test_id / bug-fix files)
- [ ] **Commit 8** — 🚀 跑小规模 eval(Supervisor vs ReAct)→ CSV → 算出 headline number → 立刻进 wayfinder 简历 bullet(依赖:API key + wayfinder + 3 MCP 可跑;在 Mac 上跑)

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
