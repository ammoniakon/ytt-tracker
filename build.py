#!/usr/bin/env python3
"""
build.py — Parse Semester_1_Quick_Reference.md → semester1.json

Run:
    python3 build.py [input.md] [output.json]
    python3 build.py                              # uses defaults below

Defaults: Semester_1_Quick_Reference.md → semester1.json

Expected per-week markdown shape:
    # WEEK N — Title (Mx)
    **Tradition focus:** ...
    **READ**
    - item...
    **LISTEN** — *inline title* or "none assigned"
    **WRITE** — *Title.* description
    - **NOTE-FILE:** `S1-WNN-slug.md`
    **PRACTICE** — description
    **TAGS:** [[T1-...]] [[T2-...]]
"""

import re
import json
import sys
from pathlib import Path
from unicodedata import normalize

HEAVY_WEEKS = {5, 10, 11}
INTEGRATION_WEEKS = {12, 13, 14}

TENSIONS_META = [
    {"id": "T1", "label": "ātman / anātman",                  "color": "#7F77DD"},
    {"id": "T2", "label": "svāsaṃvedana / vimarśa / rang rig","color": "#1D9E75"},
    {"id": "T3", "label": "prapañca / māyā",                  "color": "#E24B4A"},
    {"id": "T4", "label": "gzhi vs. ground",                  "color": "#D4537E"},
]

_TENSION_TAG_RE = re.compile(r"\\?\[\\?\[(T[1-4])[^\]]*\\?\]\\?\]", re.IGNORECASE)


# ── helpers ──────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    text = normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text[:40]


def strip_md(text: str) -> str:
    """Remove bold, italic, backtick, and link markdown."""
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text.strip()


def parse_tensions(tags_text: str) -> list:
    return sorted({m.group(1).upper() for m in _TENSION_TAG_RE.finditer(tags_text)})


# ── per-section parsers ───────────────────────────────────────────────────────

def parse_read_items(section_text: str, week_id: str) -> list:
    items = []
    for line in section_text.splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        label = strip_md(line.lstrip("- ").strip())
        if not label:
            continue
        items.append({
            "id":    f"{week_id}-READ-{slugify(label)}",
            "type":  "READ",
            "label": label,
        })
    return items


def parse_listen_items(section_text: str, week_id: str) -> list:
    if re.search(r"none assigned", section_text, re.IGNORECASE):
        return []

    items = []
    first_line = section_text.splitlines()[0]

    # Strip the **LISTEN** — prefix and *Optional:* qualifier
    first_line = re.sub(r"\*\*LISTEN\*\*\s*[—–-]\s*", "", first_line)
    first_line = re.sub(r"\*Optional[^*]*\*\s*", "", first_line).strip()

    if first_line:
        # Week 10 uses "**AND**" to separate two lectures on one line
        parts = re.split(r"\s*\*\*AND\*\*\s*", first_line)
        for part in parts:
            part = part.strip()
            # Extract **"Title"** or **Title**
            title_m = re.search(r'\*\*([^*]+)\*\*', part)
            if not title_m:
                continue
            title = title_m.group(1).strip()
            # Drop parenthetical pacing notes: (~N hr ...) or (final ~N min ...)
            title = re.split(r"\s*\(~", title)[0].strip()
            title = re.split(r"\s*\(final", title)[0].strip()
            # Drop "— first ~N minutes" suffix
            title = re.split(r"\s*[—–-]\s*first", title, flags=re.IGNORECASE)[0].strip()
            if title and title.lower() not in ("listen",):
                items.append({
                    "id":    f"{week_id}-LISTEN-{slugify(title)}",
                    "type":  "LISTEN",
                    "label": title,
                })

    # Week 12 uses bullet sub-items for optional re-listens
    for line in section_text.splitlines()[1:]:
        line = line.strip()
        if not line.startswith("-"):
            continue
        label = strip_md(line.lstrip("- ").strip())
        # Skip pacing annotations like "First half (~75 min) early in the week"
        if re.match(r"(First|Second)\s+half", label, re.IGNORECASE):
            continue
        if label:
            items.append({
                "id":    f"{week_id}-LISTEN-{slugify(label)}",
                "type":  "LISTEN",
                "label": label,
            })

    return items


def parse_write_items(section_text: str, week_id: str) -> list:
    items = []
    note_files = re.findall(r"`(S1-W\d+[ab]?-[^`]+\.md)`", section_text)

    # W11 uses numbered items: "1. *Title.* ..."
    numbered = list(re.finditer(r"^\s*\d+\.\s+\*([^*]+)\*", section_text, re.MULTILINE))

    if numbered:
        for i, m in enumerate(numbered):
            title = strip_md(m.group(1)).rstrip(".").strip()
            note_file = note_files[i] if i < len(note_files) else None
            item = {
                "id":    f"{week_id}-WRITE-{slugify(title)}",
                "type":  "WRITE",
                "label": title,
            }
            if note_file:
                item["note_file"] = note_file
            items.append(item)
    else:
        # Standard: **WRITE** — *Italic title.* description
        title_m = re.search(r"\*([^*]+)\*[.,]\s", section_text)
        if not title_m:
            # Fallback: text after "WRITE —"
            title_m = re.search(r"WRITE\*?\*?\s*[—–-]\s*([^\n.]+)", section_text)
        title = strip_md(title_m.group(1)).rstrip(".").strip() if title_m else "Written deliverable"

        note_file = note_files[0] if note_files else None
        word_m = re.search(r"(\d{3,4})[–—-](\d{3,4})\s*words?", section_text)

        item = {
            "id":    f"{week_id}-WRITE-{slugify(title)}",
            "type":  "WRITE",
            "label": title,
        }
        if note_file:
            item["note_file"] = note_file
        if word_m:
            item["word_target"] = f"{word_m.group(1)}–{word_m.group(2)} words"
        items.append(item)

    return items


def parse_practice_item(section_text: str, week_id: str) -> list:
    first = section_text.splitlines()[0]
    desc = re.sub(r"\*\*PRACTICE\*\*\s*[—–-]\s*", "", first)
    desc = strip_md(desc).strip()
    first_sentence = re.split(r"(?<=[.!?])\s", desc)[0].strip() or "Sitting practice"
    return [{
        "id":    f"{week_id}-PRACTICE-{slugify(first_sentence)[:35]}",
        "type":  "PRACTICE",
        "label": first_sentence,
    }]


# ── week-block parser ─────────────────────────────────────────────────────────

def parse_week_block(raw: str) -> dict | None:
    lines = raw.strip().splitlines()
    if not lines:
        return None

    hm = re.match(
        r"#\s+WEEK\s+(\d+)\s*[—–-]\s+(.+?)(?:\s+\(M(\w+)\))?$",
        lines[0].strip(),
    )
    if not hm:
        return None

    week_num  = int(hm.group(1))
    raw_title = hm.group(2).strip()
    module_tag = hm.group(3)   # "1", "2", … or None for integration weeks
    week_id   = f"S1-W{week_num}"

    # Split body into named sections
    sections: dict[str, list[str]] = {"header": []}
    current = "header"
    for line in lines[1:]:
        sm = re.match(r"\*\*(READ|LISTEN|WRITE|PRACTICE|TAGS)\**[:\s—–-]*(.*)", line.strip())
        if sm:
            current = sm.group(1)
            sections.setdefault(current, [])
            sections[current].append(line.strip())   # keep full line for context
        else:
            sections.setdefault(current, [])
            sections[current].append(line)

    def sec(name: str) -> str:
        return "\n".join(sections.get(name, []))

    # Tradition focus
    tf_m = re.search(r"\*\*Tradition focus:\*\*\s*(.+)", sec("header"))
    tradition = tf_m.group(1).strip() if tf_m else ""

    items: list[dict] = []
    if "READ"     in sections: items.extend(parse_read_items(sec("READ"),      week_id))
    if "LISTEN"   in sections: items.extend(parse_listen_items(sec("LISTEN"),  week_id))
    if "WRITE"    in sections: items.extend(parse_write_items(sec("WRITE"),    week_id))
    if "PRACTICE" in sections: items.extend(parse_practice_item(sec("PRACTICE"), week_id))

    return {
        "id":              week_id,
        "week_number":     week_num,
        "title":           raw_title,
        "ytt_module":      f"M{module_tag}" if module_tag else "",
        "tradition_focus": tradition,
        "is_heavy":        week_num in HEAVY_WEEKS,
        "is_integration":  week_num in INTEGRATION_WEEKS,
        "tensions":        parse_tensions(sec("TAGS")),
        "items":           items,
    }


# ── top-level ─────────────────────────────────────────────────────────────────

def parse_markdown(md_path: Path) -> dict:
    text = md_path.read_text(encoding="utf-8")
    blocks = re.split(r"(?=^#\s+WEEK\s+\d+)", text, flags=re.MULTILINE)
    weeks = []
    for block in blocks:
        if not block.strip().startswith("# WEEK"):
            continue
        w = parse_week_block(block)
        if w:
            weeks.append(w)
    weeks.sort(key=lambda w: w["week_number"])
    return {
        "semester_id": "S1",
        "title":       "YTT integration",
        "total_weeks": 14,
        "weeks":       weeks,
        "tensions":    TENSIONS_META,
    }


def verify(data: dict) -> bool:
    ok = True
    if len(data["weeks"]) != 14:
        print(f"ERROR: expected 14 weeks, got {len(data['weeks'])}", file=sys.stderr)
        ok = False
    for w in data["weeks"]:
        if len(w["items"]) < 3:
            print(f"WARNING: W{w['week_number']} has only {len(w['items'])} items", file=sys.stderr)
    return ok


def main() -> None:
    md_path  = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Semester_1_Quick_Reference.md")
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("semester1.json")

    if not md_path.exists():
        sys.exit(f"ERROR: {md_path} not found")

    print(f"Parsing {md_path} …")
    data = parse_markdown(md_path)

    print(f"Parsed {len(data['weeks'])} weeks:\n")
    for w in data["weeks"]:
        flags = ("  [HEAVY]" if w["is_heavy"] else "") + ("  [INTEGRATION]" if w["is_integration"] else "")
        print(f"  W{w['week_number']:2d}  {w['title']:<40}  {len(w['items'])} items  {w['tensions']}{flags}")

    print()
    ok = verify(data)
    if not ok:
        sys.exit(1)

    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}  ({out_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
