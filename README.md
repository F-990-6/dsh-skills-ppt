# dsh-skills-ppt

把 [ppt-master](https://github.com/hugohe3/ppt-master) 的工作流打包成 DeepSeek Harness 的一个插件：装上之后，**任何做 PPT 的需求都会自动加载这个技能**，按它的标准流程生成原生 PowerPoint。

不属于常驻提示——技能平时只是一个目录条目，被调用时才读 `SKILL.md`，所以不占每轮上下文。

## 它做什么

一句话：文档或主题 → 真正能用的 `.pptx`。

- 原生形状、转场、动画，不是图片拼贴
- 数据驱动的图表与表格
- 按演讲备注生成配音（`edge-tts`）
- 支持你自己的 `.pptx` 模板

## 安装

从 GitHub 直接装（推荐）：

```bash
dsh plugin --profile <你的 profile> add github:F-990-6/dsh-skills-ppt
```

或者先克隆到本地，再按路径装：

```bash
git clone https://github.com/F-990-6/dsh-skills-ppt.git
dsh plugin --profile <你的 profile> add ./dsh-skills-ppt
```

装完重启 DSH（新增 bundle 不会热加载）。

## 触发方式

**正常说需求就行**，识别到 PPT 相关任务会自动加载：

> 帮我把这份报告做成 PPT
> 用这个主题生成 10 页课件
> 把这份 docx 转成演示文稿
> 美化一下这个 pptx

**万一没自动触发**，在消息里加一句强制调用：

> **用 ppt-master 技能来做**

## 工作原理

插件的 `apply()` 在启动时读取包内的 `skill/ppt-master/SKILL.md`，通过 `ctx.skills.register()` 注册成一个运行时技能：

```js
ctx.skills.register({
  name: 'ppt-master',
  description,
  whenToUse,
  content: composeContent(body, layer),             // SKILL.md 正文 + DSH 层
  resourceBase: { kind: 'directory', path: dir },   // 相对路径的基准目录
  invocation: { modelInvocable: true, userInvocable: true },
})
```

因此：

- 技能出现在会话技能目录里，模型看到 `description` 和 `whenToUse` 后自行决定是否加载
- 加载后拿到的「技能基准目录」指向 `skill/ppt-master/`，里面的 `scripts/`、`templates/` 全部可用
- 不需要开启 `dsh-skill-filesystem`，也不往任何系统目录里拷文件——技能跟着插件走，卸载即消失

## 叙事骨架（DSH 层）

上游 ppt-master 管「页面怎么做」，不管「论证怎么立」。2026-10-30 的结论是：视觉高级但没有数字论证的稿子会被判不合格。所以本插件把一层 DSH 规则拼进技能正文的最前面（`skill/ppt-master/DSH_LAYER.md`，注册时注入 `content`，排在 upstream 所有章节之前），把「四拍」固定下来：

| 拍 | 页面任务 |
|---|---|
| `hook` 钩子数字 | 封面用一个可溯源数字把规模说实，标题许结果 |
| `conflict` 对立冲突 | 两个同量纲的耗时对撞，并写出因此损失什么 |
| `method` 逐条对应 | 每个方法条目对应上一页的一个耗时（`Mapping:`） |
| `evidence` 真实数据 + 边界 | 统计 + 时间窗 + 来源，并明确说清它不能证明什么 |

硬规则：任何数字必须带 `Fact IDs` / `Source` / `Data class: scenario` 之一；边界不可省；绝对成功词（全中、100%）没有分母就删掉；只做视觉的稿子会被拦。

- **触发**：客户演示、产品评审、立项 / 结项、路演、复盘、竞品对比、提案、卖点介绍。教学、参考、状态汇报默认不套，用户明确要求才套。Default 的 `design_spec.md` §III 无论套不套都记一行（`off — <原因>` 也是明确答案）；Quick 只在套用时写 `narrative.md`。
- **不想用时**：在计划里写 `- **Narrative spine**: off — <原因>`，检查器按「不适用」放行。
- **细则与反例**：`skill/ppt-master/references/dsh-narrative.md`；四页示例来自 `E:\dsh\projects\fjtcm-svc-demo_20261030`。
- **确定性检查**（Default 在 Gate 1 之后、Quick 在导出之前）：

```bash
python skill/ppt-master/scripts/dsh_narrative_check.py <项目目录> --require
```

它优先读 `design_spec.md`；若那份 spec 没记 spine 而项目里有 `narrative.md`，改读后者（Quick 的论证合同）。返回非零就改计划，不要改页面 SVG。

上游文件只增补了 `narrative.md` 的所有权登记；`SKILL.md` 一个字没动，更新上游时可干净合并。

## 依赖

技能里大量使用 Python：

```bash
python -m pip install -r skill/ppt-master/requirements.txt
```

核心是 `python-pptx`；配音需要 `edge-tts`，抓网页需要 `bs4`、`requests`。

## 目录

```
dsh-skills-ppt/
├── lib/index.js            # 插件入口：读 SKILL.md + DSH_LAYER.md 并注册技能
├── skill/ppt-master/       # 上游技能本体（SKILL.md + scripts + templates）
│   ├── DSH_LAYER.md        # 本插件加的叙事层，注册时插到技能正文最前
│   ├── references/dsh-narrative.md      # 四拍细则、字段、反例
│   └── scripts/dsh_narrative_check.py   # 叙事骨架的确定性检查
├── cordis.patch.yml        # 唯一的一行装配：插入本插件
├── package.json
└── README.md
```

`cordis.patch.yml` 不是配置，是 DSH 的装配规则——一个 bundle 必须带一个 patch 把自身这一行插进插件树。这里没有任何其它内容。

## 许可

- 本插件：MIT
- 内置的 `skill/ppt-master/`：来自 [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)，MIT，版权归原作者
- 详见 `THIRD_PARTY_NOTICES.md`
