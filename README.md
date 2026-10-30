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
  content: body,                                  // SKILL.md 正文
  resourceBase: { kind: 'directory', path: dir }, // 相对路径的基准目录
  invocation: { modelInvocable: true, userInvocable: true },
})
```

因此：

- 技能出现在会话技能目录里，模型看到 `description` 和 `whenToUse` 后自行决定是否加载
- 加载后拿到的「技能基准目录」指向 `skill/ppt-master/`，里面的 `scripts/`、`templates/` 全部可用
- 不需要开启 `dsh-skill-filesystem`，也不往任何系统目录里拷文件——技能跟着插件走，卸载即消失

## 依赖

技能里大量使用 Python：

```bash
python -m pip install -r skill/ppt-master/requirements.txt
```

核心是 `python-pptx`；配音需要 `edge-tts`，抓网页需要 `bs4`、`requests`。

## 目录

```
dsh-skills-ppt/
├── lib/index.js            # 插件入口：读 SKILL.md 并注册技能
├── skill/ppt-master/       # 上游技能本体（SKILL.md + scripts + templates）
├── cordis.patch.yml        # 唯一的一行装配：插入本插件
├── package.json
└── README.md
```

`cordis.patch.yml` 不是配置，是 DSH 的装配规则——一个 bundle 必须带一个 patch 把自身这一行插进插件树。这里没有任何其它内容。

## 许可

- 本插件：MIT
- 内置的 `skill/ppt-master/`：来自 [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)，MIT，版权归原作者
- 详见 `THIRD_PARTY_NOTICES.md`
