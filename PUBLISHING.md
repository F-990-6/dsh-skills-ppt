# 发布指南

> **当前分发方式：只用 GitHub。** 仓库已推送，安装走 `dsh plugin add github:F-990-6/dsh-skills-ppt`。
> 下文的 npm 部分是备选方案，暂时不发。

本地仓库已经初始化并完成首次提交（`main` 分支，12,871 个文件，`.git` 14.4 MB）。

## 0. 先改两处身份信息

`package.json` 里补上你自己的仓库地址，npm 页面的「Repository」链接靠它（已填好 F-990-6）：

```json
"repository": { "type": "git", "url": "git+https://github.com/<你>/dsh-skills-ppt.git" },
"homepage": "https://github.com/<你>/dsh-skills-ppt#readme",
"bugs": { "url": "https://github.com/<你>/dsh-skills-ppt/issues" }
```

## 1. 推到 GitHub

先在网页上建一个空仓库（不要勾 README / .gitignore / license，本地已经有了），然后：

```bash
cd E:/dsh/plugins/dsh-skills-ppt
git remote add origin https://github.com/<你>/dsh-skills-ppt.git
git push -u origin main
```

仓库 37.7 MB、单文件都远小于 100 MB，不需要 Git LFS。

## 2. 发到 npm

```bash
npm login                      # 浏览器里登录一次
npm publish --access public
```

`package.json` 的 `files` 已经做了白名单，只会打包 `lib/`、`skill/`、`cordis.patch.yml`、`README.md`、`LICENSE`、`THIRD_PARTY_NOTICES.md`。

**第一次发布会比较慢**（37.7 MB、13k 文件，几分钟），属于正常现象。发布前可以先看一眼将要打包的内容：

```bash
npm pack --dry-run
```

## 3. 以后怎么升级

技能本体来自上游仓库，更新走三步：

```bash
# 1) 换掉技能目录（保持同样的目录结构）
rm -rf skill/ppt-master
cp -r <上游>/skills/ppt-master skill/

# 2) 升版本（语义化：技能更新算 minor，修 bug 算 patch）
npm version minor          # 会自动 git commit + tag

# 3) 推代码、发 npm
git push --follow-tags
npm publish --access public
```

插件本身不需要改：`lib/index.js` 每次启动都重新读 `SKILL.md`，版本号也是从 frontmatter 里解析的。

## 4. 别人怎么装

```bash
dsh plugin --profile <profile> add dsh-skills-ppt
```

装完重启 DSH，之后说「帮我做个 PPT」就会自动加载。

## 5. 可选：自动发布

`.github/workflows/publish.yml`：

```yaml
name: publish
on:
  push:
    tags: ['v*']
jobs:
  npm:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          registry-url: https://registry.npmjs.org
      - run: npm publish --access public --provenance
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## 6. 发布前自查

- [ ] `package.json` 的 `name` 没被占用：`npm view dsh-skills-ppt`
- [ ] `README.md` 的安装命令和 profile 名对得上
- [ ] `THIRD_PARTY_NOTICES.md` 与 `skill/ppt-master/LICENSE` 都在
- [ ] `npm pack --dry-run` 里没有 `.git`、`.venv`、`__pycache__`
