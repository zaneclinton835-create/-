---
name: premium-a4-printable-pdf-starter
description: Use when creating a new premium A4 printable worksheet, canvas, checklist, scorecard, or report and a copyable HTML starter skeleton is needed before mapping the actual text into page roles.
---

# Premium A4 Printable PDF Starter

## Overview

Use this skill when the document type is already clear and the main need is a reliable HTML starting scaffold in the same premium print family used by the proven local PDFs. This skill gives a copyable starter skeleton and the minimum rules for adapting it safely.

## When to Use

- New worksheet/checklist/canvas/scorecard/report in the same editorial print family
- Need to start from a proven A4 HTML structure instead of rebuilding CSS each time
- Want a stable cover → chapter page → closing/review page pattern
- Need a skeleton that is Chrome-to-PDF friendly and table-driven

Do not use this skill alone when the main need is process/verification. In that case also use `premium-a4-printable-pdfs`.

## Files In This Skill

- `starter-template.html` — copyable base HTML scaffold

## Copy-First Workflow

1. Duplicate `starter-template.html` into the working directory with a document-specific filename.
2. Replace all placeholder labels, title text, and section names.
3. Map the incoming text into page roles instead of pasting it blindly.
4. Keep the CSS tokens and page shell unless there is a strong reason to change them.
5. After structure is in place, use `premium-a4-printable-pdfs` for export + verification.

## Stable House Style to Keep

- `@page { size: A4; margin: 18mm 18mm 18mm 18mm; }`
- white paper, black ink, muted gray, wine accent
- serif display headings + sans body text
- cover uses `.masthead`, `.hero-grid`, `.hero-panel`, `.stat-card`
- body uses `.chapter-intro`, `.rule`, `.folio-title`
- favor tables and simple blocks over complex CSS grid systems

## Content Mapping Rules

- **Page 1:** cover / explanation / usage context
- **Middle pages:** one clear chapter role per page or spread
- **Final page:** review / conclusion / reminder / output block
- If a section becomes a thin continuation page, convert stacked rows into a matrix or merge related blocks

## Common Mistakes

- Reintroducing a centered narrow content column and causing the old “sandwich layout”
- Using too many separate writable lines when a single matrix/table would fit better
- Treating every section equally instead of assigning page roles
- Shrinking fonts first instead of fixing structure first

## Bottom Line

Start from the scaffold, not from a blank file. Preserve the house style, map content into page roles, then use the workflow skill to export and verify.
