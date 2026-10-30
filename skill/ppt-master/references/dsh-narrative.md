# DSH Evidence Narrative

The DSH layer's argument authority for any deck whose job is to persuade. Read it
before the Stage-1 recommendations (Default) or before the roster (Quick) whenever
the request is a 客户演示 / 产品评审 / 立项 / 结项 / 路演 / 复盘 / 竞品对比 / 提案 /
卖点介绍, or any "why this exists or why it wins" request.

## 1. Decision and mode

**Test** — remove the numbers and the opposition: does the deck still persuade? If
yes, it is a reference or teaching deck and the layer does not apply. If no, it is a
persuasion deck and this layer binds.

**Record, never improvise**:

- Default: every deck records one of the two values — §III Theme Style carries
  `- **Narrative spine**: dsh-evidence-arc`, or
  `- **Narrative spine**: off — <reason the user gave>`. `off` with a reason is a
  first-class answer, not a skip.
- Quick: a persuasion deck opens `narrative.md` with `- **Spine**: dsh-evidence-arc`.

**Mode**: the four beats are not one of the five catalog presets. In Stage 1
recommend `custom` with a non-empty `Mode Behavior` (the confirmation surface rejects
`custom` without it) that states the four beats; if the user confirms a preset
instead, that preset keeps its register but the four beats and their order still
govern the roster. The spine line is recorded either way. Never invent a sixth
catalog mode or a new `mode` id.

**Opt-out** is legitimate — a status report, minutes, a teaching deck, or a reference
deck — but it is explicit, recorded, and reasoned. Silence was what produced the
feature-first deck this layer replaces.

## 2. Beat contracts

Each beat is one page. Other pages may sit between beats; each beat appears exactly
once, in this order.

### `hook` — the cover makes scale concrete

- **Must carry**: one traceable number and the outcome stated as a promise. The title
  names the outcome ("校园活动，自动抵达"), the hook line carries the number
  ("22 天里，它替你试了 547 次。").
- **Must not carry**: a category label ("XX 工具介绍"), a feature list, or an
  adjective with no measurement ("高效", "智能", "一站式").
- **Test**: a stranger can repeat the number after five seconds.

### `conflict` — why a human cannot win this by hand

- **Must carry**: two opposed quantified costs — what a person pays (time,
  attention) versus what the opportunity allows — then the loss that follows
  ("这 30 秒里，你什么都做不了"). `Relationships` states this as `contrast`.
- **Must not carry**: a qualitative-only complaint, or four or five parallel pain
  points that dilute the single opposition. One contrast, sharpened.
- **Test**: the reader can name what they lose, not merely what is inconvenient.

### `method` — one unit per cost, item by item

- **Must carry**: one ordered unit per cost named on the conflict page, and a
  `Mapping:` line stating which cost each unit removes. The title says what it does
  ("四道工序，把请求送进开放那一秒"), not what the architecture is called.
- **Must not carry**: a feature inventory, a stack tour, a unit that maps to no cost,
  or more units than the conflict page has costs.
- **Test**: delete the `Mapping:` line and the page becomes a feature list — if it
  still reads complete, the mapping was decoration.

### `evidence` — real operation data, then the boundary

- **Must carry**: measured statistics with their window and source, then an explicit
  boundary — what failed, why, and what the figure does not prove. A real deck ends
  on the concession, not on a summary or "Thank you".
- **Must not carry**: a success rate without a denominator, a hidden failure, or a
  boundary softened into reassurance ("整体表现良好").
- **Test**: the number survives a skeptical reader asking "out of how many, over what
  period, and what went wrong?".

## 3. Provenance rules

| Value kind | Label | Example |
|---|---|---|
| External measured fact | `Fact IDs: F001, F003` from `sources/*.facts.json` | 547 successful logins in the log window |
| Fact with no registry (local logs, DB, exports) | `Source:` = origin path or URL + 口径 + window + system state | `logs/抢活动.log，74,226 行，2026-10-08 至 2026-10-30，学校接口正常时段` |
| Estimate, demo KPI, illustrative figure | `Data class: scenario` and say which values | 手动一遍 ≈ 30 秒；名额"几秒"售罄 |

- A number with none of the three is a violation, not a style issue.
- Absolute claims — 全中、百发百中、稳赢、必胜、零失败、100 % — need a source on the
  same page and a denominator in the sentence, or they are removed. A negated use
  ("不是「全中」") is fine: it is the boundary, not a claim.
- Cross-check the boundary against the evidence: 74,226 log lines of which 515 say
  "no activity in the next 45 minutes" means most of the period had nothing to win.
  Saying so is the difference between evidence and advertising.

## 4. Artifact syntax

### 4.1 Default — inside `design_spec.md`

§III Theme Style:

```markdown
- **Mode**: custom — evidence arc (hook → conflict → method → evidence + boundary)
- **Narrative spine**: dsh-evidence-arc
```

§IX, one block per beat page (other fields keep their normal meaning):

```markdown
#### Slide 01 - Cover

- **Beat**: hook
- **Audience move**: 路过 → 想知道它凭什么敢跑 22 天
- **Relationships**: none
- **Title**: 校园活动，自动抵达
- **Core message**: 22 天里，它替你试了 547 次。
- **Source**: logs/抢活动.log，74,226 行，2026-10-08 至 2026-10-30

#### Slide 02 - Why it exists

- **Beat**: conflict
- **Audience move**: 觉得「手动也能抢」 → 承认手速赢不了
- **Relationships**: contrast between 手动一遍 30 秒 and 名额几秒售罄
- **Title**: 名额不等人
- **Content**: 手动一遍：打开、找活动、填信息、提交 ≈ 30 秒，这 30 秒里你什么都做不了。名额：开抢时刻全员同时点击，先到的几百人拿完；手速、网速、本机时钟误差都在扣时间。
- **Data class**: scenario — 30 秒与「几秒」是量级估计，未实测

#### Slide 03 - How it works

- **Beat**: method
- **Relationships**: order 01→04；每一步对应第 2 页的一个耗时
- **Title**: 四道工序，把请求送进开放那一秒
- **Mapping**: 01 对时 → 本机时钟误差；02 巡检 → 24 小时盯屏；03 并行 → 多个活动同时开抢；04 重试 → 被拒后的空等
- **Source**: 源码 抢活动.py / fjtcm-GrabActivities.py（对时、并行、重试），2026-10

#### Slide 04 - What it did

- **Beat**: evidence
- **Relationships**: order 统计 → 边界 → 结论
- **Title**: 22 天，它替你跑了这些
- **Content**: 547 次成功登录；545 轮自动巡检；30 次报名确认（服务器返回 200）；74,226 行运行日志。
- **Source**: logs/抢活动.log，74,226 行，2026-10-08 至 2026-10-30，学校接口正常时段
- **Boundary**: 其余尝试多数卡在 stmapi.fjtcm.edu.cn 连接超时，不是抢失败。所以 30 次不是「全中」，而是「能进的窗口里，一次没漏」。
```

When `sources/*.facts.json` exists, cite `Fact IDs: F001, ...` instead of repeating the
source; when it does not, the `Source:` line carries the origin. Estimates always say
`Data class: scenario`, in either case.

### 4.2 Quick — `narrative.md`

Quick creates no root Design Spec. The argument contract lives in `narrative.md`
instead: the spine line, then one `## Slide NN — <beat>` block per beat. It carries
arguments and provenance only — no layout, composition, resource plan, or resumable
design state.

```markdown
# Narrative Spine

- **Spine**: dsh-evidence-arc

## Slide 01 — hook

- **Beat**: hook
- **Title**: 校园活动，自动抵达
- **Claim**: 22 天里，它替你试了 547 次。
- **Source**: logs/抢活动.log，2026-10-08 至 2026-10-30

## Slide 02 — conflict

- **Beat**: conflict
- **Title**: 名额不等人
- **Relationships**: contrast between 手动 30 秒 and 名额几秒
- **Claim**: 手动 30 秒，名额几秒；人不可能 24 小时盯屏。
- **Data class**: scenario — 30 秒与「几秒」是量级估计

## Slide 03 — method

- **Beat**: method
- **Title**: 四道工序，把请求送进开放那一秒
- **Mapping**: 对时 → 时钟误差；巡检 → 盯屏；并行 → 多活动；重试 → 空等
- **Source**: 源码 抢活动.py / fjtcm-GrabActivities.py，2026-10

## Slide 04 — evidence

- **Beat**: evidence
- **Title**: 22 天，它替你跑了这些
- **Claim**: 547 次登录、545 轮巡检、30 次报名确认、74,226 行日志。
- **Source**: logs/抢活动.log，74,226 行，2026-10-08 至 2026-10-30
- **Boundary**: 失败多为接口超时，不是抢不到；30 次不是「全中」，是能进的窗口里一次没漏。
```

A complete real file ships at [`examples/narrative-evidence-arc.md`](../examples/narrative-evidence-arc.md)
— the four-page deck this layer came from, verbatim. The test suite runs it through
the checker, so a format change that breaks real files fails before it reaches a deck.

## 5. Deterministic check

`python3 ${SKILL_DIR}/scripts/dsh_narrative_check.py <project_path> [--require] [--json]`

It reads `design_spec.md`; if that spec records no spine and `narrative.md` exists, it
reads `narrative.md`. Without `--require` a deck with no spine line passes as *not
applicable*; with `--require` (the persuasion path) a missing spine fails. Codes:

| Code | Meaning |
|---|---|
| `SPINE_MISSING` | `--require` and no `Narrative spine` / `Spine` line |
| `SPINE_UNKNOWN` | Spine value is neither `dsh-evidence-arc` nor `off` |
| `BEAT_MISSING` / `BEAT_DUPLICATE` / `BEAT_ORDER` | The four beats are not exactly once each, in order |
| `BEAT_UNKNOWN` | A `Beat:` value is not `hook` / `conflict` / `method` / `evidence` |
| `HOOK_NO_NUMBER` | The hook page carries no quantity |
| `NUMBER_UNSOURCED` | A beat page has a quantity but no `Fact IDs` / `Source` / scenario label |
| `CONFLICT_NO_CONTRAST` | The conflict page's `Relationships` does not state a `contrast` |
| `METHOD_NO_MAPPING` | The method page lacks a `Mapping:` line with at least two `→` mappings |
| `EVIDENCE_NO_BOUNDARY` | The evidence page lacks a substantive `Boundary:` |
| `EVIDENCE_NOT_LAST` | A beat page follows the evidence page |
| `ABSOLUTE_CLAIM` | An absolute success claim without provenance on its page and no negation |

Repair the plan artifact, not the page: `design_spec.md` §IX (Default) or
`narrative.md` (Quick), then rerun.

## 6. Worked example — 服务号活动 四页版

The closed case this layer is derived from. Four pages, no template, dark editorial
style; the point is the argument, not the skin.

| Page | Beat | What it says | Why it works |
|---|---|---|---|
| 01 | hook | 「校园活动，自动抵达」+「22 天里，它替你试了 547 次。」 | A number the audience would never compute by hand, plus an outcome promise |
| 02 | conflict | 「手动一遍 30 秒」vs「名额几秒就没了」+「这 30 秒里，你什么都做不了」 | Two costs in the same unit of time; the loss is named |
| 03 | method | 对时 / 巡检 / 并行 / 重试，each removing 时钟误差 / 盯屏 / 单活动串行 / 被拒空等 | Every unit answers a cost from page 2; the closing line reframes the limit (手速 vs 网络往返) |
| 04 | evidence | 547 登录 / 545 巡检 / 30 报名 / 74,226 行 + boundary | A real window, a real denominator, and the failure mode admitted |

The boundary sentence is the page's payload: "其余尝试多数卡在
stmapi.fjtcm.edu.cn 连接超时，不是抢失败……不是「全中」，而是「能进的窗口里，一次没漏」。"

## 7. Closed failure cases

- **Feature-first deck** — the 3-page predecessor (01 cover, 02 `WHAT IT DOES` with
  three features, 03 `UNDER THE HOOD` with four internals) had the same visual quality
  and no argument: no number, no opposition, no evidence, no boundary. It was judged
  worse than the reference deck on content and narrative. Do not ship that shape.
- **Fabricated success** — "31 场全中" had no source and no denominator; the log
  supported 30 confirmations out of 547 logins. Absolute claims without provenance are
  removed, not softened.
- **Unmapped method** — a four-step page whose steps map to no conflict cost is a
  feature list wearing a process diagram.
- **Boundary omitted** — a deck that reports only successes reads as advertising and
  loses the trust the numbers were meant to buy.
