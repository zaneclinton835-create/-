---
name: premium-a4-printable-pdfs
description: Use when creating polished A4 printable worksheets, canvases, checklists, scorecards, or report-style documents that need a consistent editorial print style and reliable HTML-to-PDF export from local HTML.
---

# Premium A4 Printable PDFs

## Overview

Use this skill to turn structured content into a **premium, print-first A4 HTML document** and then export it to a verified PDF.

The core principle is: **design for print structure first, not web novelty**. Successful documents in this workflow used a restrained editorial system, conservative CSS, table-driven layout primitives, and an explicit export-and-density-fix loop.

## When to Use

Use this when the output is a printable document such as:
- worksheets
- canvases
- checklists
- scorecards
- review templates
- strategy / diagnosis sheets

Use this especially when the user wants:
- “same style as the previous PDF”
- premium / Harvard / McKinsey / editorial print feel
- A4 output
- HTML first, PDF second
- reliable pagination rather than flashy web styling

Do **not** use this for:
- interactive web apps
- animated landing pages
- docx-first deliverables
- presentation slides (`pptx` / slides skills are better)

## The Working House Style

Start from this print-safe baseline unless the user explicitly asks for a different direction:

### Page setup

```css
@page {
  size: A4;
  margin: 18mm 18mm 18mm 18mm;
}
```

### Color system

```css
:root {
  --paper: #ffffff;
  --ink: #0a0a0a;
  --muted: #5d5d5d;
  --soft: #8f8a80;
  --wine: #722f37;
  --gold: #b8860b;
  --rule: #e5dfd4;
  --rule-dark: #191919;
  --line: #c9c1b6;
}
```

### Typography

- Body: `"Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif`
- Display / chapter headings: `"Playfair Display", "Noto Serif SC", "Songti SC", serif`
- Typical body size: **9.15pt–9.8pt**
- Typical line-height: **1.58–1.72**

### Visual rules

- White paper background
- Black text with restrained wine accent
- Thin rules, not colored blocks
- Serif headline + sans body contrast
- No gradients, glassmorphism, shadows, floating web cards, or loud background fills

## Proven Layout Pattern

The most reliable structure is:

1. **Cover / masthead page**
2. **1–N body spreads with one clear page role each**
3. **Final review / reminder / output page**

### Cover pattern

Use a table-driven hero layout:

```css
.masthead {
  border-top: 3px solid var(--rule-dark);
  padding-top: 8mm;
  min-height: 232mm;
}

.hero-grid {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.hero-left { width: 69%; padding-right: 10mm; }
.hero-right { width: 31%; padding-left: 2mm; }
```

Cover content should usually include:
- eyebrow / small kicker
- main title
- subtitle
- dek / short purpose statement
- left-side explanation block
- right-side editorial note with 2–3 stat cards
- optional lower cover index summarizing major modules

### Body pattern

Each body page should have:
- chapter intro
- one thin rule
- 1 main information block or 1 main decision block
- compact writable structures using tables and field lines

Useful primitives:
- `.chapter-intro`
- `.chapter-index`
- `.chapter-title`
- `.chapter-lead`
- `.rule`
- `.folio-title`
- `.field-inline`
- `.metric-table`
- `.decision-table`
- `.review-panel`
- `.cover-index`

## Use Table-Driven Print Primitives

Prefer HTML tables for print stability.

### Good primitives

- cover grids
- two-column page shells
- scoring matrices
- worksheet tables
- review panels
- line-entry forms

### Avoid

- CSS grid as primary print layout
- floating sidebars
- absolute-position ornaments
- large colored boxes for section backgrounds

Conservative print HTML was the stable choice across the proven documents.

## Content Mapping Rules

Before writing HTML, map the content into **page roles**, not just section order.

Examples:
- worksheet / scorecard → cover + scoring page + judgment page + review page
- checklist packet → cover + one dense scenario per page + closing review page
- strategy canvas → cover + grouped concept spreads + commitment / quick-sheet / example pages

If a page feels thin, do **not** immediately shrink the whole document. First ask:
- Can two sections be grouped onto one page?
- Can a right-side note become a full-width bottom band?
- Can repeated field lines become a matrix?
- Can reminder content be merged into the appendix / review page?

## The Anti-Patterns We Already Hit

### 1. “Sandwich layout”

Root cause:
- centered narrow content column
- colored middle content boxes

Fix:
- full-width white paper feel
- transparent or minimal section backgrounds
- remove narrow-column center-box effect

### 2. Thin continuation pages

Root cause:
- repeated field rows consuming vertical space
- one section spilling by just a small amount

Fix:
- convert stacked fields into compact tables / matrices
- reduce only local block spacing or writable row height
- re-export and verify again

### 3. Underused pages

Root cause:
- cover page with too little lower-page structure
- review pages with too few writable regions
- compact commitment/tracker blocks using too little vertical area

Fix:
- add cover index or bottom summary band
- enlarge the functional writable block
- move dense explanatory elements into lower-page bands

## Density Workflow

Always fix density **structurally first**, globally second.

### First-choice fixes

- merge related sections
- turn 9 field lines into a 3-row matrix
- enlarge useful writable areas
- reduce large intro spacing
- convert side explanation into bottom strip or review panel

### Only then use a gentle density pass

Typical safe reductions:
- body font: reduce by `0.15pt–0.25pt`
- line-height: reduce slightly
- `chapter-intro` bottom margin: reduce by `1mm`
- `rule` bottom margin: reduce by `1mm`
- writable cell height: reduce locally

Do **not** aggressively shrink the entire document on the first attempt.

## Export Command

Use headless Chrome for export:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless \
  --disable-gpu \
  --allow-file-access-from-files \
  --no-pdf-header-footer \
  --print-to-pdf="/absolute/path/output.pdf" \
  "file:///absolute/path/input.html"
```

This was the stable export path across the proven documents.

## Verification Loop

Never stop at “HTML written”. Always verify all of these:

### 1. Parse HTML

```bash
python3 - <<'PY'
from html.parser import HTMLParser
from pathlib import Path
class P(HTMLParser):
    pass
p = P()
p.feed(Path('/absolute/path/file.html').read_text(encoding='utf-8'))
print('HTML parse OK')
PY
```

### 2. Check PDF metadata

```bash
mdls -name kMDItemNumberOfPages -name kMDItemPageWidth -name kMDItemPageHeight "/absolute/path/file.pdf"
```

### 3. Inspect rendered pages

Use a visual inspection tool to verify:
- actual page count
- page order
- no blank pages
- no thin continuation pages
- no clipped sections
- no odd underused pages

### 4. If pagination is wrong

Do not guess. Identify the exact culprit block and fix that block only.

## Slash-Command Style Workflow

The command model should be **one primary entry point**, not three equal commands.

### `/premium-pdf`

Use this as the default command whenever the request is effectively “收到文本 → 生成 html → 导出 pdf → 验证”.

**Input:** raw text, outline, worksheet copy, checklist copy, scorecard copy, or report text.

**Default flow:**

1. **Receive text**
   - Preserve the supplied text faithfully.
   - Decide page roles before touching HTML.
   - Choose the density target: compact worksheet vs editorial document.

2. **Generate HTML**
   - Start from the proven house style or `premium-a4-printable-pdf-starter`.
   - Map content into cover / body / closing roles.
   - Favor structural layout moves first: tables, matrices, grouped sections, review panels.

3. **Export PDF**
   - Run the actual Chrome export command from `## Export Command`.
   - Do not stop at “HTML is done”.

4. **Verify**
   - Parse the HTML.
   - Check A4 and page count with `mdls`.
   - Visually inspect the rendered PDF.
   - Specifically look for sandwich layout, thin continuation pages, blank pages, clipping, and underused pages.

5. **Repair if needed**
   - Fix structure first.
   - Only then do small density reductions.
   - Re-export and re-verify.

### Submodes

Use submodes only when the user explicitly wants a partial pass instead of the full pipeline.

- `/premium-pdf verify-only`
  - Skip new layout work.
  - Only inspect the existing HTML/PDF pair.
  - Check parse status, A4 metadata, page count, blank pages, thin continuation pages, clipping, and underused pages.

- `/premium-pdf compact-only`
  - Do not redesign the whole document.
  - Focus only on density and page-usage improvements.
  - Fix structure first, then small spacing/font reductions, then re-export and re-verify.

### Short command version

`/premium-pdf = receive text → map page roles → build html → export pdf → mdls check → visual check → structural fix if needed → re-export`

### Input Examples

Use `/premium-pdf` when the user gives you complete text and clearly wants a printable deliverable.

Examples:

- `/premium-pdf`
  - Input: “把这段课程配套资料做成 PDF，风格和前面的 premium A4 一样。”

- `/premium-pdf`
  - Input: “这是完整提纲：封面、A、B、C、D，请直接生成 HTML 和 PDF。”

- `/premium-pdf verify-only`
  - Input: “帮我检查这个 PDF 有没有空白页、薄续页、裁切问题。”

- `/premium-pdf compact-only`
  - Input: “这个 PDF 总体很好，但有些页面空间利用率太低，优化一下。”

### Natural-Language Trigger Map

Map ordinary user phrasing into the command automatically.

| User says | Route to |
|---|---|
| “把这段内容做成 pdf” | `/premium-pdf` |
| “按刚才那个风格再做一份” | `/premium-pdf` |
| “生成 html 再导出 pdf” | `/premium-pdf` |
| “帮我检查分页 / 空白页 / 裁切” | `/premium-pdf verify-only` |
| “这个版式太松了 / 空间利用率太低” | `/premium-pdf compact-only` |
| “别重做，只检查一下” | `/premium-pdf verify-only` |
| “别改内容，只压紧一点” | `/premium-pdf compact-only` |

## Fast Build Checklist

- [ ] Map the content into page roles before writing HTML
- [ ] Use the white / black / wine editorial print system
- [ ] Use table-driven layout primitives
- [ ] Build a real cover page, not just a title page
- [ ] Keep each body page to one clear role
- [ ] Export with headless Chrome
- [ ] Parse HTML before claiming success
- [ ] Verify A4 metadata
- [ ] Visually inspect pagination
- [ ] Fix local density issues structurally before global shrinking

## Common Mistakes

| Mistake | Better move |
|---|---|
| Narrow centered content area | Use full-page white-paper composition |
| Colored middle panels | Use rules and typography instead |
| Nine stacked field lines | Convert to matrix/table |
| Thin continuation page | Compress the exact spilling block |
| Sparse cover | Add cover index or lower-page support structure |
| Global font shrinking first | Fix the local page-role problem first |

## Output Naming Pattern

When making sibling deliverables, create:
- one standalone HTML per document
- one standalone PDF per document
- descriptive filenames that match the visible title

Recommended convention:

- **working HTML filename:** stable, ASCII-friendly, kebab-case
- **final PDF filename:** user-facing Chinese title is allowed when that improves usability

Naming rule:

`working-slug.html` → `final-display-name.pdf`

Examples:
- `six-scenario-checklist.html` → `six-scenario-checklist.pdf`
- `problem-diagnostic-tool.html` → `问题诊断工具.pdf`
- `battlefield-selection-matrix.html` → `战场选择矩阵（虚实×优势）.pdf`

## Bottom Line

The repeatable pattern is:

**editorial cover + page-role-based body planning + conservative table-driven print HTML + Chrome export + density-fix loop guided by actual rendered pages**.

That combination produced the stable, premium-looking A4 PDFs in this workflow.
