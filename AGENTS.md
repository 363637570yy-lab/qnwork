# Agent notes — 工程工作台

本仓库做的是 **QNwork**（工程工作台，机电投标第一刀），不是维护上游 Grok App。
产品名、窗口名、桌面快捷方式一律是 QNwork。远程与自动更新只认 `https://github.com/363637570yy-lab/qnwork`。
`origin` 推本仓；`upstream` 只 fetch `RongleCat/grok-app`。吸收上游见方案 §7.6，冲突时品牌和更新地址不退回 Grok App。
产品方案已修订冻结：[`docs/工程工作台目标方案.md`](docs/工程工作台目标方案.md)。改需求先改方案，不要只改代码。

上游 Grok App 的 wiki / 需求 / plans 已移出本仓库文档区。改壳时以方案第 4 节和下面「改壳」为准。

---

## 产品边界

- 用户：造价 / 机电 / 投标。选定招标包 → 选任务 → 得到可复核的 Word / Excel。
- 对话与改文件：本机已登录的 Grok Build CLI（`grok agent stdio` / ACP）。
- 点位、延长米、金额：Python 脚本计算。模型只写特征、说明、答疑表述。
- 壳不内嵌模型，不自研对话循环，不改 Grok Build 源码。
- 第一版 sidecar 只接 `grok`。换 Claude / Codex 放到后续版本。
- 本期不做：广联达 GBQ 二进制、网页版、全专业 BIM、Computer Use 去点 CAD / 广联达。

## 出数纪律

1. **资料只读。** 业主 / 设计院招标包不写回。产物只写平级 `DXF/<项目名>/AI生成资料/`（成品）和 `DXF/<项目名>/.analysis/`（底稿）。
2. **打开哪个目录。** 会话信任招标包；`output_root` 用已有 `layout.py` 推到平级 `DXF/<项目名>`，并给这条路径写权限。
3. **MCP 是能力，Skill 是流程，侧栏只认任务目录。** 能出数 / 出文件的先做 MCP；Skill 只写何时调、禁止再 `python xx.py`；新任务加目录行，不改壳。
4. **出数任务必须 `invoke: direct`。** 壳按目录直调同一 MCP，再把摘要贴回会话。禁止只丢一句 prompt。按钮和对话禁止两套出数逻辑。
5. **v0.1 只保证新汇园。** 复现现有内部清单 xlsx + 广联达 xlsx，数量与当前 `.analysis` 脚本产出一致。不宣称换包也能算。
6. **先适配、不重写算法。** 现有 `takeoff` / `quote` / `glodon` 数量多为人工誊录，不是管道自动算。包装时只做路径参数和返回值（`ok` / `files[]` / `qty_summary` / `open_items[]` / `log_path`）。失败必须返回原因，禁止静默写空表。
7. **没有 takeoff 结果，模型不得填写工程数量。** 管件、支吊架等图纸不可见项标暂估，进入 `open_items`。信息价必须注明月份与来源。
8. **索引是前置。** 没有 `index.json` 就不要跑 takeoff。索引用已有 `engineering-project-analysis`（`survey` → `index_drawings` → `extract_facts`），不要在项目目录里另写一套。

## 改壳

本仓库根目录就是桌面壳源码。工程任务侧栏、成果面板是本项目功能；Remote IM、皮肤包、ChatCut、SSH、15 语言跟齐、发版刷贡献者头像，都不是。

- 新 UI 放独立模块（`src/components/`、`src/hooks/`、`src/providers/`、`src/lib/`）。不要往 `src/App.tsx` / `src/app/AppWorkbench.tsx` 堆 `useState` 或大块功能。
- 禁止 `window.confirm` / `prompt` / `alert`，禁止原生 `<select>` 和系统右键菜单。复用现有 Modal / Select / ContextMenu。
- 默认 shared 模式（`GROK_HOME=~/.grok`）**不得改写**用户已有 `~/.grok`。工程 MCP / Skill 放项目级 `.grok/`，或独立 `GROK_HOME`。
- 产品名 QNwork。`productName` / 窗口标题 / `app.name` 不要再写 Grok。identifier 用 `com.qnwork.desktop`（开发 `com.qnwork.desktop.dev`），禁止继续用 `com.grokapp.desktop`。
- 安装包 identifier / AUMID / app-data 必须与用户已装的 Grok / Grok App 分开。
- 仓库与更新：`package.json`、`app_update.rs`、`useUpdater.ts` 默认指向 `363637570yy-lab/qnwork`。不要把检查更新指回 `RongleCat/grok-app`。
- 关于页必须标明：壳为社区 Grok App 改版；核为本机 Grok Build CLI；非 xAI 官方产品。
- 界面文案：第一版 `zh` 为准，`en` 可占位。不要为工程任务去补齐上游 15 套语言。
- 粘贴的 UUID 默认当 App 会话 id，不当 CLI agent id。
- 侧栏按任务目录渲染，不要写死五个按钮。成果面板只认 MCP 统一出参。
- 按钮必须走完整忙 / 错 / 空路径，并且真的按目录直调 MCP 出文件。只摆入口不算完成。

## 资产落点

| 位置 | 内容 |
| --- | --- |
| `docs/工程工作台目标方案.md` | 修订冻结的产品方案 |
| 本仓库根目录 | 桌面壳源码（原 grok-app 树） |
| `D:\BCKF\CAD\.claude\skills\engineering-project-analysis\` | 勘察 / 索引 / 事实库 / 路径布局 |
| `D:\BCKF\CAD\DXF\新汇园89号楼超级创业者社区场景验证测试平台二期工程\.analysis\` | v0.1 对照脚本与已生成表 |

招标包不进 git。不要提交密钥、`auth.json`、本机 agent home。
