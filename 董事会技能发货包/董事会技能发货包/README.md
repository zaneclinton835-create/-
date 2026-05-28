# 董事会技能发货包

这是一套可直接交付的 Codex/Codex App 技能包，包含：

- `expert-council` 董事会技能
- 13 位默认专家技能
- 精美 PDF 相关技能

## 包含内容

`skills/` 目录下共包含以下技能：

- `expert-council`
- `munger-perspective`
- `elon-musk-perspective`
- `taleb-perspective`
- `dalio-perspective`
- `soros-perspective`
- `andrew-ng-perspective`
- `taiichi-ohno-perspective`
- `zhangxiaolong-perspective`
- `jeff-bezos-perspective`
- `peter-thiel-perspective`
- `andy-grove-perspective`
- `howard-marks-perspective`
- `reid-hoffman-perspective`
- `premium-a4-printable-pdfs`
- `premium-a4-printable-pdf-system`
- `premium-a4-printable-pdf-starter`

## 安装方式

把本包里的 `skills/` 目录内容，复制到对方机器的 Codex 技能目录即可。

常见目标目录：

- `~/.codex/skills/`
- 或 `$CODEX_HOME/skills/`

最终应当是这样的结构：

```text
~/.codex/skills/expert-council/SKILL.md
~/.codex/skills/jeff-bezos-perspective/SKILL.md
~/.codex/skills/peter-thiel-perspective/SKILL.md
...
```

## 使用建议

### 1. 直接调用董事会

用户可以直接说：

- “调用董事会讨论这个问题”
- “让董事会帮我做一次决策会诊”
- “请用专家组讨论并输出 PDF”

`expert-council` 会自动在专家池里选 3 位最合适的专家出席。

### 2. 单独调用专家

也可以直接单独调用：

- “用贝索斯的视角看这个问题”
- “用 Thiel 的视角分析”
- “用 Howard Marks 的角度判断现在该不该出手”

## PDF 导出依赖

`expert-council` 的 PDF 渲染依赖 Chromium 内核浏览器。

当前版本会自动探测以下浏览器：

- Google Chrome
- Chromium
- Microsoft Edge

如果自动探测不到，可以手动设置环境变量：

```bash
export EXPERT_COUNCIL_CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
```

## 额外说明

- `expert-council` 已经内置 premium A4 PDF 工作流，不是普通网页打印件。
- 如果机器上有 `pdfinfo` / `pdftotext`，质检会更完整；没有也能运行，只是部分 PDF 页面检查会降级。
- 本包默认适合 Mac / Unix 风格目录环境；如果交付给 Windows 用户，建议额外提供一份安装说明。

## 发货建议

推荐同时发给用户两样东西：

1. 这个完整技能包
2. 一份你自己的案例 PDF 或案例截图

这样用户能同时看到：

- 技能本体
- 实际效果

