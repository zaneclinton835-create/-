#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from html import escape
from html.parser import HTMLParser
from pathlib import Path


TARGET_ATTENDEE_WEIGHT = 1650
TARGET_DISCUSSION_WEIGHT = 2400
MIN_PAGE_UTILIZATION = 0.46
MIN_BODY_FONT_SIZE_PT = 10.6

LAYOUT_PROFILES = [
    {
        "name": "default",
        "body_font_pt": 10.8,
        "css": "",
    },
    {
        "name": "cover-tight",
        "body_font_pt": 10.8,
        "css": """
        .masthead { min-height: 212mm; }
        .cover-verdict { margin-top: 5mm; padding: 2.8mm 0 3mm 0; }
        .cover-attendees { margin-top: 2.2mm; padding-bottom: 2.4mm; }
        .cover-attendees-list { font-size: 8.8pt; }
        .cover-index { margin-top: 6mm; gap: 2.6mm 7mm; }
        .hero-meta { margin-top: 5.5mm; }
        """,
    },
    {
        "name": "section-tight",
        "body_font_pt": 10.8,
        "css": """
        .chapter-intro { margin-bottom: 4mm; }
        .rule { margin-bottom: 4mm; }
        .attendee-stack { gap: 7mm; }
        .discussion-block { margin-bottom: 6mm; }
        .exchange { margin-bottom: 3.8mm; }
        .decision-memo { margin-bottom: 5mm; }
        .footer { margin-top: 5mm; }
        """,
    },
    {
        "name": "micro-tight",
        "body_font_pt": 10.6,
        "css": """
        html, body { font-size: 10.6pt; line-height: 1.68; }
        .hero-title { font-size: 23.2pt; }
        .chapter-title { font-size: 20.6pt; }
        .speaker { font-size: 12.8pt; }
        .cover-index { margin-top: 5.5mm; }
        .discussion-block { margin-bottom: 5.2mm; }
        .exchange { margin-bottom: 3.4mm; }
        """,
    },
]


def clean(text: str) -> str:
    return escape((text or "").strip())


def resolve_chrome_path() -> str:
    env_path = os.environ.get("EXPERT_COUNCIL_CHROME_PATH") or os.environ.get("CHROME_PATH")
    if env_path and Path(env_path).exists():
        return env_path

    candidate_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    for candidate in candidate_paths:
        if Path(candidate).exists():
            return candidate

    for command_name in [
        "google-chrome",
        "google-chrome-stable",
        "chromium",
        "chromium-browser",
        "chrome",
        "msedge",
    ]:
        resolved = shutil.which(command_name)
        if resolved:
            return resolved

    raise FileNotFoundError(
        "Chrome/Chromium not found. Set EXPERT_COUNCIL_CHROME_PATH to your browser executable."
    )


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[-\s]+", "-", text.strip().lower())
    return text or "expert-council"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def remove_if_exists(path: Path) -> None:
    if path.exists():
        path.unlink()


def html_parse_ok(path: Path) -> dict:
    class Parser(HTMLParser):
        pass

    parser = Parser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return {"ok": True}


def pdfinfo_fallback(pdf_path: Path) -> dict:
    try:
        result = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        info = {}
        for line in result.stdout.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            info[key.strip()] = value.strip()
        return {
            "pages": info.get("Pages"),
            "page_size": info.get("Page size"),
        }
    except Exception:
        return {"error": "pdfinfo failed or not found"}


def mdls_pdf(pdf_path: Path) -> dict:
    info_fallback = pdfinfo_fallback(pdf_path)
    try:
        subprocess.run(["mdimport", str(pdf_path)], check=True, capture_output=True, text=True)
    except Exception:
        pass

    try:
        result = subprocess.run(
            [
                "mdls",
                "-name",
                "kMDItemNumberOfPages",
                "-name",
                "kMDItemPageWidth",
                "-name",
                "kMDItemPageHeight",
                str(pdf_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = {}
        for line in result.stdout.splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            payload[key.strip()] = value.strip()
        if any(str(v).strip() == "(null)" for v in payload.values()):
            return info_fallback
        if info_fallback.get("pages") and info_fallback.get("page_size"):
            return {
                "pages": info_fallback.get("pages"),
                "page_size": info_fallback.get("page_size"),
            }
        return payload
    except Exception:
        return info_fallback


def parse_page_count(pdf_checks: dict) -> int | None:
    raw = str(pdf_checks.get("pages", "")).strip()
    match = re.search(r"\d+", raw)
    return int(match.group()) if match else None


def page_role(page_no: int, attendee_pages: int, discussion_pages: int, total_pages: int) -> str:
    if page_no == 1:
        return "cover"
    if page_no <= 1 + attendee_pages:
        return "attendee"
    if page_no <= 1 + attendee_pages + discussion_pages:
        return "discussion"
    if page_no == total_pages:
        return "decision"
    return "unknown"


def extract_pdf_page_texts(pdf_path: Path, page_count: int | None) -> list[str]:
    if not page_count:
        return []
    texts: list[str] = []
    for page_no in range(1, page_count + 1):
        try:
            result = subprocess.run(
                ["pdftotext", "-f", str(page_no), "-l", str(page_no), str(pdf_path), "-"],
                check=True,
                capture_output=True,
                text=True,
            )
            texts.append(compact_text(result.stdout))
        except Exception:
            return []
    return texts


def inspect_pdf_pages(pdf_path: Path, attendee_pages: int, discussion_pages: int, pdf_checks: dict) -> dict:
    page_count = parse_page_count(pdf_checks)
    texts = extract_pdf_page_texts(pdf_path, page_count)
    if not texts:
        return {
            "page_count": page_count,
            "page_text_checks_available": False,
            "blank_pages": [],
            "underused_pages": [],
            "page_text_lengths": [],
        }

    thresholds = {
        "cover": 120,
        "attendee": 260,
        "discussion": 320,
        "decision": 180,
        "unknown": 220,
    }
    blank_pages = []
    underused_pages = []
    page_text_lengths = []
    total_pages = len(texts)
    for page_no, text in enumerate(texts, start=1):
        role = page_role(page_no, attendee_pages, discussion_pages, total_pages)
        length = len(text)
        page_text_lengths.append({"page": page_no, "role": role, "chars": length})
        if length <= 12:
            blank_pages.append(page_no)
            continue
        if length < thresholds.get(role, 220):
            underused_pages.append({"page": page_no, "role": role, "chars": length})

    return {
        "page_count": total_pages,
        "page_text_checks_available": True,
        "blank_pages": blank_pages,
        "underused_pages": underused_pages,
        "page_text_lengths": page_text_lengths,
    }


def evaluate_quality_gate(profile: dict, layout_checks: dict, pdf_checks: dict, page_checks: dict) -> dict:
    issues = []
    expected_pages = 2 + layout_checks.get("attendee_pages", 0) + layout_checks.get("discussion_pages", 0)
    actual_pages = page_checks.get("page_count") or parse_page_count(pdf_checks)

    if actual_pages and expected_pages != actual_pages:
        issues.append(
            {
                "code": "page_count_mismatch",
                "detail": f"expected {expected_pages} pages from layout plan, got {actual_pages}",
            }
        )

    if layout_checks.get("thin_pages_detected"):
        issues.append(
            {
                "code": "thin_layout_groups",
                "detail": "layout estimator found thin attendee/discussion pages",
            }
        )

    if page_checks.get("blank_pages"):
        issues.append(
            {
                "code": "blank_pages",
                "detail": f"blank PDF pages detected: {page_checks.get('blank_pages')}",
            }
        )

    if page_checks.get("underused_pages"):
        issues.append(
            {
                "code": "underused_pages",
                "detail": f"underused pages detected: {page_checks.get('underused_pages')}",
            }
        )

    if profile.get("body_font_pt", 0) < MIN_BODY_FONT_SIZE_PT:
        issues.append(
            {
                "code": "font_too_small",
                "detail": f"body font fell below floor {MIN_BODY_FONT_SIZE_PT}pt",
            }
        )

    return {
        "passed": not issues,
        "expected_pages": expected_pages,
        "actual_pages": actual_pages,
        "issues": issues,
    }


def run_chrome_export(html_path: Path, pdf_path: Path) -> None:
    chrome_path = resolve_chrome_path()

    subprocess.run(
        [
            chrome_path,
            "--headless",
            "--disable-gpu",
            "--allow-file-access-from-files",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            html_path.resolve().as_uri(),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def stat_card(label: str, value: str) -> str:
    return (
        '<div class="stat-card">'
        f'<div class="stat-label">{clean(label)}</div>'
        f'<div class="stat-value">{clean(value)}</div>'
        "</div>"
    )


def paragraphize(text: str) -> str:
    blocks = [seg.strip() for seg in re.split(r"\n{2,}", text or "") if seg.strip()]
    if not blocks:
        return ""
    return "".join(f"<p>{clean(block)}</p>" for block in blocks)


def render_inline_paragraphs(text: str) -> str:
    blocks = [seg.strip() for seg in re.split(r"\n{2,}", text or "") if seg.strip()]
    if not blocks:
        return ""
    return "".join(f"<p>{clean(block)}</p>" for block in blocks)


def excerpt_text(text: str, limit: int = 120) -> str:
    normalized = compact_text(text)
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "…"


def strip_stage_prefix(text: str) -> str:
    value = (text or "").strip()
    if not value:
        return ""
    patterns = [
        r"^\s*round\s*\d+\s*[|｜:：-]\s*",
        r"^\s*阶段\s*\d+\s*[|｜:：-]\s*",
        r"^\s*第[一二三四五六七八九十0-9]+轮\s*[|｜:：-]?\s*",
        r"^\s*(phase|hearing|segment)\s*\d+\s*[|｜:：-]\s*",
    ]
    for pattern in patterns:
        value = re.sub(pattern, "", value, flags=re.IGNORECASE)
    return value.strip() or text.strip()


def compact_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def estimate_text_weight(text: str) -> int:
    normalized = compact_text(text)
    if not normalized:
        return 0
    return len(normalized)


def estimate_attendee_weight(attendee: dict) -> int:
    text_weight = estimate_text_weight(attendee.get("why_selected", "")) + estimate_text_weight(attendee.get("initial_take", ""))
    # Attendee cards carry substantial HTML structural overhead
    # (name/role headers, block-label, card wrapper, stack grid).
    # A 1.6× multiplier on text weight plus a higher base better
    # predicts actual Chrome-rendered weight and prevents
    # single-page overflow that produces thin continuation pages.
    return int(text_weight * 1.6) + 400


def estimate_section_weight(section: dict) -> int:
    total = 260 + estimate_text_weight(section.get("title", "")) + estimate_text_weight(section.get("summary", ""))
    for exchange in section.get("exchanges", []):
        total += estimate_exchange_weight(exchange)
    return total


def estimate_exchange_weight(exchange: dict) -> int:
    return (
        220
        + estimate_text_weight(exchange.get("speaker", ""))
        + estimate_text_weight(exchange.get("target", ""))
        + estimate_text_weight(exchange.get("text", ""))
    )


def split_section_for_layout(section: dict, target_weight: int = 1180) -> list[dict]:
    exchanges = section.get("exchanges", [])
    if not exchanges:
        return [section]

    blocks = []
    current_exchanges = []
    current_weight = 220 + estimate_text_weight(section.get("title", "")) + estimate_text_weight(section.get("summary", ""))
    for exchange in exchanges:
        exchange_weight = estimate_exchange_weight(exchange)
        if current_exchanges and current_weight + exchange_weight > target_weight:
            blocks.append(current_exchanges)
            current_exchanges = [exchange]
            current_weight = 160 + estimate_text_weight(section.get("title", ""))
        else:
            current_exchanges.append(exchange)
        current_weight += exchange_weight
    if current_exchanges:
        blocks.append(current_exchanges)

    if len(blocks) == 1:
        return [section]

    split_sections = []
    for index, chunk in enumerate(blocks, start=1):
        title = section.get("title", "")
        if index > 1:
            title = f"{title}（续）"
        split_sections.append(
            {
                "title": title,
                "summary": section.get("summary", "") if index == 1 else "",
                "exchanges": chunk,
            }
        )
    return split_sections


def get_discussion_layout_blocks(data: dict) -> list[dict]:
    blocks = []
    for section in get_discussion_sections(data):
        blocks.extend(split_section_for_layout(section))
    return blocks


def group_by_weight(items: list[dict], target_weight: int, estimator) -> list[list[dict]]:
    groups: list[list[dict]] = []
    current: list[dict] = []
    current_weight = 0
    for item in items:
        item_weight = estimator(item)
        if current and current_weight + item_weight > target_weight:
            groups.append(current)
            current = [item]
            current_weight = item_weight
            continue
        current.append(item)
        current_weight += item_weight
    if current:
        groups.append(current)
    return groups


def rebalance_groups(groups: list[list[dict]], target_weight: int, estimator) -> list[list[dict]]:
    if len(groups) < 2:
        return groups
    last_weight = sum(estimator(item) for item in groups[-1])
    if last_weight / target_weight >= MIN_PAGE_UTILIZATION:
        return groups
    previous_weight = sum(estimator(item) for item in groups[-2])
    if previous_weight + last_weight <= int(target_weight * 1.28):
        return groups[:-2] + [groups[-2] + groups[-1]]
    return groups


def normalize_discussion_sections(data: dict) -> tuple[list[dict], bool]:
    used_legacy = False
    sections = data.get("discussion_flow")
    if not sections:
        sections = data.get("debate_rounds", [])
        used_legacy = bool(sections)

    normalized = []
    for index, section in enumerate(sections, start=1):
        title = strip_stage_prefix(section.get("label") or section.get("title") or f"讨论片段 {index}")
        summary = compact_text(section.get("purpose") or section.get("summary") or "")
        turns = section.get("turns") or section.get("exchanges") or []
        normalized_turns = []
        for turn in turns:
            speaker = compact_text(turn.get("speaker", ""))
            target = compact_text(turn.get("target", ""))
            text = (turn.get("text") or "").strip()
            normalized_turns.append(
                {
                    "speaker": speaker,
                    "target": target,
                    "text": text,
                }
            )
        normalized.append(
            {
                "title": title,
                "summary": summary,
                "exchanges": normalized_turns,
            }
        )
    return normalized, used_legacy


def normalize_report_data(data: dict) -> tuple[dict, dict]:
    normalized = dict(data)
    sections, used_legacy = normalize_discussion_sections(data)
    normalized["discussion_flow"] = [
        {
            "label": section["title"],
            "purpose": section["summary"],
            "turns": section["exchanges"],
        }
        for section in sections
    ]
    normalized.pop("debate_rounds", None)
    normalized["attendees"] = [
        {
            "name": compact_text(attendee.get("name", "")),
            "role": compact_text(attendee.get("role", "")),
            "why_selected": (attendee.get("why_selected") or "").strip(),
            "initial_take": (attendee.get("initial_take") or "").strip(),
        }
        for attendee in data.get("attendees", [])
    ]
    if "chair" in normalized:
        chair = dict(normalized.get("chair") or {})
        chair["action_items"] = [compact_text(item) for item in chair.get("action_items", []) if compact_text(item)]
        normalized["chair"] = chair

    checks = {
        "used_legacy_rounds": used_legacy,
        "discussion_sections": len(sections),
        "attendees": len(normalized.get("attendees", [])),
    }
    return normalized, checks


def get_discussion_sections(data: dict) -> list[dict]:
    sections, _ = normalize_discussion_sections(data)
    return sections


def review_layout(attendee_groups: list[list[dict]], discussion_groups: list[list[dict]]) -> dict:
    attendee_utilization = [
        round(sum(estimate_attendee_weight(item) for item in group) / TARGET_ATTENDEE_WEIGHT, 2)
        for group in attendee_groups
    ]
    discussion_utilization = [
        round(sum(estimate_section_weight(item) for item in group) / TARGET_DISCUSSION_WEIGHT, 2)
        for group in discussion_groups
    ]
    return {
        "attendee_pages": len(attendee_groups),
        "discussion_pages": len(discussion_groups),
        "attendee_page_utilization": attendee_utilization,
        "discussion_page_utilization": discussion_utilization,
        "thin_pages_detected": any(u < MIN_PAGE_UTILIZATION for u in attendee_utilization + discussion_utilization),
    }


def chunked(items: list, size: int) -> list[list]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def build_cover(data: dict, page_no: int) -> str:
    attendees = data.get("attendees", [])
    sections = get_discussion_sections(data)
    chair = data.get("chair", {})
    cards = [
        stat_card("出席董事", str(len(attendees))),
        stat_card("讨论片段", str(len(sections))),
        stat_card("听证模式", data.get("hearing_mode", "full-hearing")),
    ]
    cover_index = "".join(
        f'<div class="index-item"><span class="index-k">{i:02d}</span>'
        f"<span>{clean(item)}</span></div>"
        for i, item in enumerate(
            [
                "议题摘要与主席定位",
                "出席专家与初始陈词",
                "完整圆桌讨论记录",
                "主席裁决与执行动作",
            ],
            start=1,
        )
    )
    verdict_excerpt = excerpt_text(chair.get("final_decision", ""), 144)
    attendee_strip = " · ".join(clean(item.get("name", "")) for item in attendees if item.get("name"))
    return f"""
    <section class="spread cover">
      <div class="page-body">
        <div class="masthead">
          <div class="eyebrow">Expert Council Memo</div>
          <table class="hero-grid">
            <tr>
              <td class="hero-left">
                <div class="hero-title">{clean(data.get("topic", "Expert Council"))}</div>
                <div class="hero-subtitle">{clean(data.get("one_line_case", ""))}</div>
                <div class="hero-dek">
                  这份报告保留完整讨论过程，并将专家分歧压缩为可执行判断。
                  目标不是制造舞台化冲突，而是把真实共识、真实分歧与动作优先级写清楚。
                </div>
                <div class="hero-meta">
                  <div><span class="meta-label">日期</span>{clean(data.get("date", ""))}</div>
                  <div><span class="meta-label">模式</span>{clean(data.get("hearing_mode", ""))}</div>
                </div>
              </td>
              <td class="hero-right">
                <div class="side-note">
                  <div class="side-title">结论预览</div>
                  <div class="side-copy">
                    {clean(verdict_excerpt)}
                  </div>
                  <div class="stat-stack">
                    {''.join(cards)}
                  </div>
                </div>
              </td>
            </tr>
          </table>
          <div class="cover-verdict">
            <div class="cover-verdict-title">主席先行判断</div>
            <div class="cover-verdict-copy">{clean(verdict_excerpt)}</div>
          </div>
          <div class="cover-attendees">
            <span class="cover-attendees-label">本次出席</span>
            <span class="cover-attendees-list">{attendee_strip}</span>
          </div>
          <div class="cover-index">
            {cover_index}
          </div>
        </div>
      </div>
      <div class="footer">
        <span>Board Discussion Record</span>
        <span>{page_no:02d}</span>
      </div>
    </section>
    """


def build_attendee_spreads(data: dict, start_page_no: int) -> tuple[list[str], list[list[dict]]]:
    spreads: list[str] = []
    attendees = data.get("attendees", [])
    attendee_groups = rebalance_groups(
        group_by_weight(attendees, TARGET_ATTENDEE_WEIGHT, estimate_attendee_weight),
        TARGET_ATTENDEE_WEIGHT,
        estimate_attendee_weight,
    )
    for group_index, attendee_group in enumerate(attendee_groups, start=1):
        lead = (
            "每位董事先独立表态。这里保留各自的判断逻辑，而不是让主持人代替他们说话。"
            if group_index == 1
            else "这一页继续记录其余董事的开场判断，保持阅读连续，而不是把短内容切成大量薄页。"
        )
        blocks = []
        for attendee in attendee_group:
            blocks.append(
                f"""
                <section class="attendee-block">
                  <div class="attendee-card-head">
                    <div class="attendee-index"></div>
                    <div class="attendee-meta">
                      <div class="attendee-name">{clean(attendee.get("name", ""))}</div>
                      <div class="attendee-role">{clean(attendee.get("role", ""))}</div>
                    </div>
                  </div>
                  <div class="attendee-reason">
                    <div class="block-label">选入原因</div>
                    <div>{clean(attendee.get("why_selected", ""))}</div>
                  </div>
                  <div class="attendee-body">
                    <div class="block-label">初始陈词</div>
                    {paragraphize(attendee.get("initial_take", ""))}
                  </div>
                </section>
                """
            )
        spreads.append(
            f"""
            <section class="spread">
              <div class="page-body">
                <div class="chapter-intro">
                  <div class="folio-title">Attendees & Initial Statements</div>
                  <div class="chapter-title">出席董事与初始判断</div>
                  <div class="chapter-lead">{lead}</div>
                </div>
                <div class="rule"></div>
                <div class="attendee-stack">
                  {''.join(blocks)}
                </div>
              </div>
              <div class="footer">
                <span>Initial Statements</span>
                <span>{start_page_no + group_index - 1:02d}</span>
              </div>
            </section>
            """
        )
    return spreads, attendee_groups


def build_round_spread(round_index: int, round_data: dict) -> str:
    exchanges = []
    for item in round_data.get("exchanges", []):
        exchanges.append(
            f"""
            <div class="exchange">
              <div class="exchange-head">
                <span class="speaker">{clean(item.get("speaker", ""))}</span>
                <span class="target">回应 {clean(item.get("target", ""))}</span>
              </div>
              <div class="exchange-text">{paragraphize(item.get("text", ""))}</div>
            </div>
            """
        )
    return f"""
    <section class="spread">
      <div class="page-body">
        <div class="chapter-intro">
          <div class="folio-title">Board Discussion Record</div>
          <div class="chapter-title">{clean(round_data.get("title", f"Round {round_index}"))}</div>
          <div class="chapter-lead">{clean(round_data.get("summary", ""))}</div>
        </div>
        <div class="rule"></div>
        <div class="exchange-list">
          {''.join(exchanges)}
        </div>
      </div>
      <div class="footer">
        <span>Discussion Segment {round_index:02d}</span>
        <span>{round_index:02d}</span>
      </div>
    </section>
    """


def build_discussion_spreads(data: dict, start_page_no: int) -> tuple[list[str], list[list[dict]]]:
    spreads: list[str] = []
    sections = get_discussion_layout_blocks(data)
    discussion_groups = rebalance_groups(
        group_by_weight(sections, TARGET_DISCUSSION_WEIGHT, estimate_section_weight),
        TARGET_DISCUSSION_WEIGHT,
        estimate_section_weight,
    )
    for group_index, section_group in enumerate(discussion_groups, start=1):
        section_html = []
        for section in section_group:
            exchanges = []
            for item in section.get("exchanges", []):
                target_text = f"回应 {clean(item.get('target', ''))}" if item.get("target") else ""
                exchanges.append(
                    f"""
                    <div class="exchange">
                      <div class="exchange-head">
                        <span class="speaker">{clean(item.get("speaker", ""))}</span>
                        <span class="target">{target_text}</span>
                      </div>
                      <div class="exchange-text">{paragraphize(item.get("text", ""))}</div>
                    </div>
                    """
                )
            section_html.append(
                f"""
                <section class="discussion-block">
                  <div class="discussion-kicker">{clean(section.get("title", ""))}</div>
                  <div class="discussion-summary">{clean(section.get("summary", ""))}</div>
                  <div class="exchange-list">
                    {''.join(exchanges)}
                  </div>
                </section>
                """
            )
        spreads.append(
            f"""
            <section class="spread">
              <div class="page-body">
                <div class="chapter-intro">
                  <div class="folio-title">Boardroom Transcript</div>
                  <div class="chapter-title">讨论实录</div>
                  <div class="chapter-lead">以下保留真实讨论的推进顺序，不再把会话伪装成整齐的问答模板。</div>
                </div>
                <div class="rule"></div>
                <div class="discussion-stack">
                  {''.join(section_html)}
                </div>
              </div>
              <div class="footer">
                <span>Discussion Transcript</span>
                <span>{start_page_no + group_index - 1:02d}</span>
              </div>
            </section>
            """
        )
    return spreads, discussion_groups


def build_decision_spread(data: dict, page_no: int) -> str:
    chair = data.get("chair", {})
    narrative_blocks = []
    if chair.get("counter_intuitive_truth"):
        narrative_blocks.append(f"需要特别记住的一点是：{chair.get('counter_intuitive_truth', '')}")
    if chair.get("tail_risk_mitigation"):
        narrative_blocks.append(f"这件事最大的风险不在表面波动，而在于：{chair.get('tail_risk_mitigation', '')}")
    if chair.get("protect_first"):
        narrative_blocks.append(f"如果判断错了，优先保护的是：{chair.get('protect_first', '')}")
    narrative_html = render_inline_paragraphs("\n\n".join(narrative_blocks))
    action_items = "".join(f"<li>{clean(item)}</li>" for item in chair.get("action_items", []))
    return f"""
    <section class="spread">
      <div class="page-body">
        <div class="chapter-intro">
          <div class="folio-title">Chairman&apos;s Memo</div>
          <div class="chapter-title">主席结论</div>
          <div class="chapter-lead">
            这一页保留会议结束时真正会被带走的判断，不把结论拆成机械表单。
          </div>
        </div>
        <div class="rule"></div>
        <div class="memo-highlight">
          <div class="memo-kicker">本次拍板</div>
          <div class="memo-highlight-copy">{clean(chair.get("final_decision", ""))}</div>
        </div>
        <div class="decision-memo">
          {narrative_html}
        </div>
        <div class="action-panel">
          <div class="block-label">先做这几件事</div>
          <ol class="action-list">
            {action_items}
          </ol>
        </div>
      </div>
      <div class="footer">
        <span>Chair Memo</span>
        <span>{page_no:02d}</span>
      </div>
    </section>
    """


BASE_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    @page {{
      size: A4;
      margin: 18mm 18mm 18mm 18mm;
    }}
    :root {{
      --paper: #ffffff;
      --ink: #0a0a0a;
      --muted: #5d5d5d;
      --soft: #8f8a80;
      --wine: #722f37;
      --rule: #e5dfd4;
      --rule-dark: #191919;
      --line: #c9c1b6;
    }}
    * {{
      box-sizing: border-box;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }}
    html, body {{
      margin: 0;
      padding: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
      font-size: 10.8pt;
      line-height: 1.72;
    }}
    body {{
      counter-reset: spread;
    }}
    p {{
      margin: 0 0 3.5mm 0;
    }}
    .spread {{
      position: relative;
      min-height: 260mm;
      page-break-after: always;
      break-after: page;
      display: flex;
      flex-direction: column;
    }}
    .page-body {{
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: 0;
    }}
    .spread:last-child {{
      page-break-after: auto;
      break-after: auto;
    }}
    .masthead {{
      border-top: 3px solid var(--rule-dark);
      padding-top: 7mm;
      min-height: 218mm;
    }}
    .eyebrow, .folio-title {{
      color: var(--wine);
      letter-spacing: 0.16em;
      font-size: 7.9pt;
      text-transform: uppercase;
      font-weight: 700;
    }}
    .hero-grid {{
      width: 100%;
      table-layout: fixed;
      border-collapse: collapse;
      margin-top: 4mm;
    }}
    .hero-left {{
      width: 69%;
      padding-right: 10mm;
      vertical-align: top;
    }}
    .hero-right {{
      width: 31%;
      padding-left: 2mm;
      vertical-align: top;
    }}
    .hero-title, .chapter-title, .decision-title {{
      font-family: "Playfair Display", "Noto Serif SC", "Songti SC", serif;
      font-size: 24pt;
      line-height: 1.14;
      font-weight: 700;
      letter-spacing: 0.01em;
      margin: 2mm 0 4mm 0;
    }}
    .hero-subtitle {{
      font-size: 12.4pt;
      font-weight: 600;
      line-height: 1.64;
      max-width: 108mm;
      margin-bottom: 4mm;
    }}
    .hero-dek, .chapter-lead, .side-copy {{
      color: var(--muted);
    }}
    .hero-meta {{
      margin-top: 7mm;
      display: grid;
      grid-template-columns: 1fr;
      gap: 1.6mm;
      font-size: 9.2pt;
    }}
    .meta-label {{
      display: inline-block;
      min-width: 17mm;
      color: var(--soft);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 7.6pt;
      margin-right: 2mm;
    }}
    .side-note {{
      border-top: 1.2px solid var(--rule-dark);
      border-bottom: 1px solid var(--rule);
      padding: 4mm 0;
    }}
    .side-title {{
      font-family: "Playfair Display", "Noto Serif SC", "Songti SC", serif;
      font-size: 13.8pt;
      margin-bottom: 2.4mm;
    }}
    .cover-verdict {{
      margin-top: 6mm;
      border-top: 1px solid var(--rule-dark);
      border-bottom: 1px solid var(--rule);
      padding: 3mm 0 3.2mm 0;
    }}
    .cover-verdict-title {{
      color: var(--wine);
      letter-spacing: 0.12em;
      text-transform: uppercase;
      font-size: 7.4pt;
      font-weight: 700;
      margin-bottom: 1.6mm;
    }}
    .cover-verdict-copy {{
      font-size: 10.6pt;
      line-height: 1.64;
      max-width: 145mm;
    }}
    .cover-attendees {{
      margin-top: 2.8mm;
      display: flex;
      gap: 3mm;
      align-items: baseline;
      border-bottom: 1px solid var(--rule);
      padding-bottom: 2.8mm;
    }}
    .cover-attendees-label {{
      color: var(--wine);
      letter-spacing: 0.12em;
      text-transform: uppercase;
      font-size: 7.4pt;
      font-weight: 700;
      white-space: nowrap;
    }}
    .cover-attendees-list {{
      color: var(--muted);
      font-size: 9pt;
      line-height: 1.5;
    }}
    .stat-stack {{
      display: grid;
      gap: 2.6mm;
      margin-top: 5mm;
    }}
    .stat-card {{
      border-top: 1px solid var(--line);
      padding-top: 2.4mm;
    }}
    .stat-label {{
      color: var(--soft);
      font-size: 7.5pt;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin-bottom: 0.8mm;
    }}
    .stat-value {{
      font-family: "Playfair Display", "Noto Serif SC", "Songti SC", serif;
      font-size: 16.5pt;
      line-height: 1.1;
    }}
    .cover-index {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 3mm 8mm;
      border-top: 1px solid var(--rule);
      margin-top: 8mm;
      padding-top: 3mm;
    }}
    .index-item {{
      display: flex;
      gap: 3mm;
      align-items: baseline;
      font-size: 9pt;
    }}
    .index-k {{
      color: var(--wine);
      font-family: "Playfair Display", "Noto Serif SC", "Songti SC", serif;
      font-size: 11.2pt;
      min-width: 8mm;
    }}
    .chapter-intro {{
      padding-top: 3mm;
      margin-bottom: 5mm;
    }}
    .chapter-title {{
      font-size: 21.5pt;
      margin-bottom: 2.5mm;
    }}
    .rule {{
      border-top: 1px solid var(--rule-dark);
      margin-bottom: 5mm;
    }}
    .attendee-meta {{
      display: block;
      border-top: 1px solid var(--rule-dark);
      padding-top: 3mm;
      margin-bottom: 3.2mm;
    }}
    .attendee-card-head {{
      display: grid;
      grid-template-columns: 10mm 1fr;
      gap: 4mm;
      align-items: start;
    }}
    .attendee-index {{
      border-top: 1px solid var(--rule-dark);
      padding-top: 3.3mm;
      position: relative;
    }}
    .attendee-index::before {{
      content: "";
      display: block;
      width: 4.5mm;
      height: 4.5mm;
      border-radius: 50%;
      background: var(--wine);
      margin-top: 1.2mm;
      opacity: 0.9;
    }}
    .attendee-stack {{
      display: grid;
      gap: 8mm;
      flex: 1;
    }}
    .attendee-block {{
      display: flex;
      flex-direction: column;
    }}
    .attendee-name {{
      font-family: "Playfair Display", "Noto Serif SC", "Songti SC", serif;
      font-size: 17.2pt;
      line-height: 1.15;
      margin-bottom: 1.2mm;
    }}
    .attendee-role {{
      color: var(--muted);
      font-size: 9pt;
    }}
    .attendee-reason {{
      margin-bottom: 4mm;
      color: var(--muted);
    }}
    .block-label {{
      display: block;
      color: var(--wine);
      letter-spacing: 0.12em;
      text-transform: uppercase;
      font-size: 7.5pt;
      margin-bottom: 0.9mm;
      font-weight: 700;
    }}
    .attendee-body {{
      page-break-inside: avoid;
    }}
    .exchange-list {{
      display: block;
      flex: 1;
    }}
    .discussion-stack {{
      display: block;
      flex: 1;
    }}
    .discussion-block {{
      display: block;
      margin-bottom: 8mm;
      break-inside: auto;
    }}
    .discussion-kicker {{
      color: var(--wine);
      font-size: 8.6pt;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      font-weight: 700;
      margin-bottom: 1.6mm;
    }}
    .discussion-summary {{
      color: var(--muted);
      margin-bottom: 2.6mm;
    }}
    .exchange {{
      border-top: 1px solid var(--line);
      padding-top: 2.7mm;
      margin-bottom: 4.5mm;
      break-inside: avoid;
    }}
    .exchange-head {{
      display: flex;
      justify-content: space-between;
      gap: 5mm;
      align-items: baseline;
      margin-bottom: 1.3mm;
      font-size: 8.8pt;
    }}
    .speaker {{
      font-family: "Playfair Display", "Noto Serif SC", "Songti SC", serif;
      font-size: 13.2pt;
      line-height: 1.15;
    }}
    .target {{
      color: var(--soft);
    }}
    .decision-memo {{
      display: block;
      margin-bottom: 6mm;
    }}
    .decision-memo p {{
      margin-bottom: 4mm;
    }}
    .memo-highlight {{
      border-top: 1.5px solid var(--rule-dark);
      border-bottom: 1px solid var(--rule);
      padding: 3mm 0 3.5mm 0;
      margin-bottom: 5mm;
    }}
    .memo-kicker {{
      color: var(--wine);
      letter-spacing: 0.12em;
      text-transform: uppercase;
      font-size: 7.4pt;
      font-weight: 700;
      margin-bottom: 1.6mm;
    }}
    .memo-highlight-copy {{
      font-family: "Playfair Display", "Noto Serif SC", "Songti SC", serif;
      font-size: 12.2pt;
      line-height: 1.5;
    }}
    .action-panel {{
      margin-top: auto;
      border-top: 1.5px solid var(--rule-dark);
      padding-top: 3mm;
    }}
    .action-list {{
      margin: 0;
      padding-left: 5.6mm;
    }}
    .action-list li {{
      margin-bottom: 2.2mm;
    }}
    .footer {{
      display: flex;
      justify-content: space-between;
      gap: 5mm;
      margin-top: 6mm;
      padding-top: 2mm;
      border-top: 1px solid var(--rule);
      color: var(--soft);
      font-size: 7.8pt;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    {profile_css}
  </style>
</head>
<body>
{body}
</body>
</html>
"""


def build_full_report_html(data: dict, profile: dict | None = None) -> tuple[str, dict]:
    profile = profile or LAYOUT_PROFILES[0]
    attendee_pages, attendee_groups = build_attendee_spreads(data, start_page_no=2)
    discussion_start = 2 + len(attendee_pages)
    discussion_pages, discussion_groups = build_discussion_spreads(data, start_page_no=discussion_start)
    decision_page_no = discussion_start + len(discussion_pages)
    body = [build_cover(data, page_no=1), *attendee_pages, *discussion_pages, build_decision_spread(data, page_no=decision_page_no)]
    html = BASE_TEMPLATE.format(
        title=clean(data.get("topic", "Expert Council")),
        body="".join(body),
        profile_css=profile.get("css", ""),
    )
    return html, review_layout(attendee_groups, discussion_groups)


def build_final_decision_html(data: dict, profile: dict | None = None) -> str:
    profile = profile or LAYOUT_PROFILES[0]
    chair = data.get("chair", {})
    actions = "".join(f"<li>{clean(item)}</li>" for item in chair.get("action_items", []))
    memo_parts = []
    if chair.get("final_decision"):
        memo_parts.append(chair.get("final_decision", ""))
    if chair.get("counter_intuitive_truth"):
        memo_parts.append(f"需要特别记住的一点是：{chair.get('counter_intuitive_truth', '')}")
    if chair.get("tail_risk_mitigation"):
        memo_parts.append(f"最大的风险在于：{chair.get('tail_risk_mitigation', '')}")
    if chair.get("protect_first"):
        memo_parts.append(f"如果后面判断有偏差，先保护：{chair.get('protect_first', '')}")
    memo_html = render_inline_paragraphs("\n\n".join(memo_parts))
    body = f"""
    <section class="spread cover">
      <div class="page-body">
        <div class="masthead">
          <div class="eyebrow">Chair Memo Brief</div>
          <table class="hero-grid">
            <tr>
              <td class="hero-left">
                <div class="hero-title">{clean(data.get("topic", ""))}</div>
                <div class="hero-subtitle">{clean(data.get("one_line_case", ""))}</div>
                <div class="hero-dek">
                  这是面向执行的主席备忘录摘要版，只保留最后需要带走的判断和先手动作。
                </div>
              </td>
              <td class="hero-right">
                <div class="side-note">
                  <div class="side-title">结论摘录</div>
                  <div class="side-copy">{clean(chair.get("counter_intuitive_truth", ""))}</div>
                  <div class="stat-stack">
                    {stat_card("日期", data.get("date", ""))}
                    {stat_card("模式", data.get("hearing_mode", ""))}
                  </div>
                </div>
              </td>
            </tr>
          </table>
        </div>
      </div>
      <div class="footer">
        <span>Chair Memo Summary</span>
        <span>01</span>
      </div>
    </section>
    <section class="spread">
      <div class="page-body">
        <div class="chapter-intro">
          <div class="folio-title">Chairman&apos;s Memo</div>
          <div class="chapter-title">主席结论</div>
          <div class="chapter-lead">
            这一版适合直接阅读结论、带着动作去执行，不再把结论拆成标签式问答。
          </div>
        </div>
        <div class="rule"></div>
        <div class="decision-memo">
          {memo_html}
        </div>
        <div class="action-panel">
          <div class="block-label">先做这几件事</div>
          <ol class="action-list">{actions}</ol>
        </div>
      </div>
      <div class="footer">
        <span>Chair Memo</span>
        <span>02</span>
      </div>
    </section>
    """
    return BASE_TEMPLATE.format(
        title=clean(data.get("topic", "Final Decision")),
        body=body,
        profile_css=profile.get("css", ""),
    )


def render_with_quality_gate(
    data: dict,
    output_dir: Path,
    final_report_pdf_path: Path,
    keep_intermediates: bool,
    max_auto_polish: int,
) -> tuple[dict, dict, dict, dict, str]:
    attempts = []
    selected_profile = None
    selected_html = ""
    selected_html_checks = {}
    selected_layout = {}
    selected_pdf = {}
    selected_page_checks = {}
    selected_quality_gate = {}

    profiles = LAYOUT_PROFILES[: max(1, min(max_auto_polish, len(LAYOUT_PROFILES)))]

    with tempfile.TemporaryDirectory(prefix="expert-council-") as tmpdir:
        tmpdir_path = Path(tmpdir)
        for attempt_no, profile in enumerate(profiles, start=1):
            temp_html = tmpdir_path / f"{profile['name']}.html"
            temp_pdf = tmpdir_path / f"{profile['name']}.pdf"
            html, layout_checks = build_full_report_html(data, profile=profile)
            write_file(temp_html, html)
            html_checks = {"council_report": html_parse_ok(temp_html)}
            run_chrome_export(temp_html, temp_pdf)
            pdf_checks = {"council_report": mdls_pdf(temp_pdf)}
            page_checks = inspect_pdf_pages(
                temp_pdf,
                attendee_pages=layout_checks.get("attendee_pages", 0),
                discussion_pages=layout_checks.get("discussion_pages", 0),
                pdf_checks=pdf_checks["council_report"],
            )
            quality_gate = evaluate_quality_gate(profile, layout_checks, pdf_checks["council_report"], page_checks)
            attempts.append(
                {
                    "attempt": attempt_no,
                    "profile": profile["name"],
                    "layout": layout_checks,
                    "pdf": pdf_checks["council_report"],
                    "pages": page_checks,
                    "quality_gate": quality_gate,
                }
            )
            if quality_gate["passed"]:
                shutil.copy2(temp_pdf, final_report_pdf_path)
                selected_profile = profile["name"]
                selected_html = html
                selected_html_checks = html_checks
                selected_layout = layout_checks
                selected_pdf = pdf_checks
                selected_page_checks = page_checks
                selected_quality_gate = quality_gate
                if keep_intermediates:
                    write_file(output_dir / "council-report.html", html)
                break

        if not selected_profile and attempts:
            last_attempt = attempts[-1]
            fallback_html = build_full_report_html(data, profile=profiles[-1])[0]
            write_file(tmpdir_path / "last-failed.html", fallback_html)
            run_chrome_export(tmpdir_path / "last-failed.html", final_report_pdf_path)
            if keep_intermediates:
                write_file(output_dir / "council-report.html", fallback_html)
            selected_profile = last_attempt["profile"]
            selected_html = fallback_html
            selected_html_checks = {"council_report": html_parse_ok(tmpdir_path / "last-failed.html")}
            selected_layout = last_attempt["layout"]
            selected_pdf = {"council_report": mdls_pdf(final_report_pdf_path)}
            selected_page_checks = inspect_pdf_pages(
                final_report_pdf_path,
                attendee_pages=selected_layout.get("attendee_pages", 0),
                discussion_pages=selected_layout.get("discussion_pages", 0),
                pdf_checks=selected_pdf["council_report"],
            )
            selected_quality_gate = evaluate_quality_gate(
                profiles[-1],
                selected_layout,
                selected_pdf["council_report"],
                selected_page_checks,
            )

    quality_checks = {
        "passed": selected_quality_gate.get("passed", False),
        "selected_profile": selected_profile,
        "auto_polish_applied": len(attempts) > 1,
        "attempts": attempts,
        "final_page_checks": selected_page_checks,
        "final_gate": selected_quality_gate,
    }
    return (
        {"council_report": html_parse_ok(output_dir / "council-report.html")} if keep_intermediates else selected_html_checks,
        selected_pdf,
        selected_layout,
        quality_checks,
        selected_profile or profiles[-1]["name"],
    )


def build_manifest(
    output_dir: Path,
    html_checks: dict,
    pdf_checks: dict,
    data: dict,
    normalization_checks: dict,
    layout_checks: dict,
    contract_checks: dict,
    quality_checks: dict,
) -> dict:
    return {
        "topic": data.get("topic"),
        "date": data.get("date"),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "output_dir": str(output_dir),
        "artifacts": {
            "report_json": str(output_dir / "report.json"),
            "council_report_pdf": str(output_dir / "council-report.pdf"),
        },
        "checks": {
            "normalization": normalization_checks,
            "layout": layout_checks,
            "quality_gate": quality_checks,
            "html": html_checks,
            "pdf": pdf_checks,
            "output_contract": contract_checks,
        },
    }


def enforce_output_contract(output_dir: Path, keep_intermediates: bool) -> dict:
    forbidden_root_html = []
    for artifact in output_dir.parent.iterdir():
        if artifact.is_file() and artifact.suffix.lower() == ".html":
            forbidden_root_html.append(str(artifact))
    contract = {
        "keep_intermediates": keep_intermediates,
        "forbidden_root_html_detected": forbidden_root_html,
    }
    if forbidden_root_html:
        contract["warning"] = "Detected standalone HTML files outside the council report directory."
    return contract


def main() -> None:
    parser = argparse.ArgumentParser(description="Render expert council JSON into premium A4 HTML/PDF.")
    parser.add_argument("--input", required=True, help="Path to report.json")
    parser.add_argument("--output-dir", required=True, help="Directory for rendered artifacts")
    parser.add_argument("--keep-intermediates", action="store_true", help="Keep HTML and summary artifacts.")
    parser.add_argument(
        "--max-auto-polish",
        type=int,
        default=len(LAYOUT_PROFILES),
        help="Maximum number of built-in layout repair passes before failing the quality gate.",
    )
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    ensure_dir(output_dir)

    raw_data = read_json(input_path)
    data, normalization_checks = normalize_report_data(raw_data)

    final_report_pdf_path = output_dir / "council-report.pdf"
    report_json_path = output_dir / "report.json"
    manifest_path = output_dir / "manifest.json"
    full_html_path = output_dir / "council-report.html"
    final_html_path = output_dir / "final-decision.html"
    final_pdf_path = output_dir / "final-decision.pdf"

    write_file(report_json_path, json.dumps(data, ensure_ascii=False, indent=2))
    html_checks, pdf_checks, layout_checks, quality_checks, selected_profile = render_with_quality_gate(
        data=data,
        output_dir=output_dir,
        final_report_pdf_path=final_report_pdf_path,
        keep_intermediates=args.keep_intermediates,
        max_auto_polish=args.max_auto_polish,
    )

    if args.keep_intermediates:
        profile = next((item for item in LAYOUT_PROFILES if item["name"] == selected_profile), LAYOUT_PROFILES[0])
        final_decision_html = build_final_decision_html(data, profile=profile)
        write_file(final_html_path, final_decision_html)
        html_checks["final_decision"] = html_parse_ok(final_html_path)
        run_chrome_export(final_html_path, final_pdf_path)
        pdf_checks["final_decision"] = mdls_pdf(final_pdf_path)
    else:
        remove_if_exists(full_html_path)
        remove_if_exists(final_html_path)
        remove_if_exists(final_pdf_path)
        remove_if_exists(output_dir / "full-report.html")
        remove_if_exists(output_dir / "full-report.pdf")
        remove_if_exists(output_dir / "final-decision.html")
        remove_if_exists(output_dir / "final-decision.pdf")

    contract_checks = enforce_output_contract(output_dir, args.keep_intermediates)
    manifest = build_manifest(
        output_dir,
        html_checks,
        pdf_checks,
        data,
        normalization_checks,
        layout_checks,
        contract_checks,
        quality_checks,
    )
    write_file(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2))

    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    if not quality_checks.get("passed"):
        raise SystemExit("Quality gate failed; built-in auto-polish passes did not reach the required PDF standard.")


if __name__ == "__main__":
    main()
