---
name: premium-a4-printable-pdf-system
description: Use when working with the premium A4 printable PDF skill set and a quick overview is needed for which skill to use first, how the pieces fit together, and what the default workflow is.
---

# Premium A4 Printable PDF System

## Overview

This is the top-level overview for the premium A4 printable PDF workflow.

Use it when you want to understand the system quickly instead of opening the starter skill and workflow skill separately.

The system has **two working parts**:

1. `premium-a4-printable-pdf-starter`
   - gives you the copyable HTML scaffold
   - use first when you need a new document skeleton

2. `premium-a4-printable-pdfs`
   - gives you the full workflow
   - use when you are ready to map text, export PDF, verify, and repair pagination/density

## Which One Should I Use?

### Start with `premium-a4-printable-pdf-starter` when:

- you are creating a new worksheet / checklist / canvas / scorecard / report from scratch
- you want the proven HTML shell immediately
- you need a copyable A4 premium-print starting point

### Start with `premium-a4-printable-pdfs` when:

- you already have text and need the complete pipeline
- you need export / verification / compact-pass behavior
- the problem is no longer “how do I start the HTML?” but “how do I finish the document correctly?”

## Default Mental Model

The normal workflow is:

`text → page-role mapping → HTML → PDF export → metadata check → visual check → local repair if needed`

That means:

- structure before styling tweaks
- tables and print-safe blocks before fancy layout
- PDF verification before any completion claim

## Default Command Path

If you only remember one command concept, remember this:

- **default:** `/premium-pdf`

Submodes are optional:

- `/premium-pdf verify-only`
- `/premium-pdf compact-only`

## Short Usage Guide

### Case 1 — New document from raw text

1. Open `premium-a4-printable-pdf-starter`
2. Copy the scaffold
3. Map the text into page roles
4. Switch to `premium-a4-printable-pdfs`
5. Run the full `/premium-pdf` workflow

### Case 2 — Existing HTML, need PDF only

1. Open `premium-a4-printable-pdfs`
2. Use `/premium-pdf`

### Case 3 — Existing PDF, needs inspection only

1. Open `premium-a4-printable-pdfs`
2. Use `/premium-pdf verify-only`

### Case 4 — Existing PDF is too loose / too sparse

1. Open `premium-a4-printable-pdfs`
2. Use `/premium-pdf compact-only`

## Natural Language Routing

Treat these as equivalent triggers:

- “按之前那个 premium A4 风格做一个 PDF” → `premium-a4-printable-pdfs`
- “给我一个可复制的 HTML 起手骨架” → `premium-a4-printable-pdf-starter`
- “帮我检查这个 PDF 有没有薄续页 / 空白页” → `premium-a4-printable-pdfs`
- “这个 PDF 空间利用率太低，压紧一点” → `premium-a4-printable-pdfs`

## File Map

- `/Users/cuiqingsong/.claude/skills/premium-a4-printable-pdf-starter/SKILL.md`
- `/Users/cuiqingsong/.claude/skills/premium-a4-printable-pdf-starter/starter-template.html`
- `/Users/cuiqingsong/.claude/skills/premium-a4-printable-pdfs/SKILL.md`

## Bottom Line

If you need a shell, use the **starter** skill.
If you need the full production loop, use the **workflow** skill.
If unsure, start from the starter, then finish with the workflow.
