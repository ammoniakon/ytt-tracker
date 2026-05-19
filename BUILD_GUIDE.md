# YTT Curriculum Tracker — Build Guide & Semester Template

This document captures the full process for deploying a new semester of the tracker, from planning through live deployment. It is written for someone who has done this before and needs a structured reference, not a step-by-step tutorial.

---

## Architecture Overview

The tracker is a single self-contained HTML file (`tracker_v2.html`) with two embedded data structures:

1. **`#semester-data`** (`<script type="application/json">`) — the curriculum skeleton: weeks, item IDs, labels, types. This is what renders in the UI.
2. **`READINGS` object** (inside the main `<script>` block) — the info-modal content: reading details, writing prompts, recording tips. Keyed by item ID. Items without a READINGS entry get a dim ⓘ button; items with one get a lit ⓘ button.

State (status circles) lives in `localStorage` and optionally syncs to Supabase. Supabase credentials are stored as constants near the top of the `<script>` block.

---

## ID Naming Convention

Every item has a unique ID structured as:

```
S{semester}-W{week}-{TYPE}-{slug}
```

- `S1` = Semester 1, `S2` = Semester 2, etc.
- `W1`–`W14` = week number (no zero-padding in the ID)
- `TYPE` = `READ`, `LISTEN`, `WRITE`, `RECORD`, `PRACTICE`
- `slug` = short kebab-case description, truncated to ~45 characters

**Examples:**
```
S2-W1-READ-module-b-wk-1-mmk-preface-intro
S2-W3-LISTEN-malcolm-akbh-s1c2
S2-W5-WRITE-fascia-as-prana-medium-audit
S2-W7-RECORD-module-focused-class-youtube
```

IDs must be globally unique within the file. If you reuse a text from a prior semester, give it a new semester prefix.

---

## Curriculum Data Structure (`#semester-data`)

Located near line 620. The full structure:

```json
{
  "semester_id": "S2",
  "title": "Your semester title",
  "total_weeks": 14,
  "weeks": [
    {
      "id": "S2-W1",
      "week_number": 1,
      "title": "Week Theme Name",
      "ytt_module": "M1",
      "tradition_focus": "One-sentence description of what each thread covers this week.",
      "is_heavy": false,
      "is_integration": false,
      "tensions": ["T1", "T3"],
      "items": [
        // item objects — see Item Templates below
      ]
    }
    // ... repeat for each week
  ]
}
```

**`is_heavy`** — marks the week with a visual indicator (heavy reading load).  
**`is_integration`** — marks synthesis/capstone weeks (W12–W14 typically).  
**`tensions`** — T1 through T4 are the four philosophical tension codes from the curriculum design; tag each week with which tensions are activated.

---

## Item Templates (Curriculum Data)

### READ
```json
{
  "id": "S2-W1-READ-source-slug",
  "type": "READ",
  "label": "Author, Title: passage description"
}
```

### LISTEN
```json
{
  "id": "S2-W1-LISTEN-source-slug",
  "type": "LISTEN",
  "label": "Speaker, Talk Title"
}
```

### WRITE (with prompt)
```json
{
  "id": "S2-W1-WRITE-essay-slug",
  "type": "WRITE",
  "label": "*Essay title",
  "note_file": "S2-W01-essay-slug.md",
  "word_target": "500–700 words"
}
```

### WRITE (recurring — no prompt needed)
```json
{
  "id": "S2-W1-WRITE-self-reflections",
  "type": "WRITE",
  "label": "Self-Reflections"
},
{
  "id": "S2-W1-WRITE-discussion-responses",
  "type": "WRITE",
  "label": "Discussion Responses"
}
```

### RECORD
```json
{
  "id": "S2-W4-RECORD-module-focused-class-youtube",
  "type": "RECORD",
  "label": "Record: module-focused class (YouTube)"
}
```

### PRACTICE
```json
{
  "id": "S2-W1-PRACTICE-slug",
  "type": "PRACTICE",
  "label": "Practice description."
}
```

---

## READINGS Object Templates

Located starting around line 1930 (after the semester data). Each entry is keyed by item ID. Add new semester entries in a coherent block before the closing `};` of the READINGS object.

### READ — primary text
```js
"S2-W1-READ-source-slug": {
  "source": "Full title of work",
  "author": "Author name",
  "translator": "Translator name (Publisher, year)",
  "edition": "Publisher, year, volume/page info",
  "passage": "Specific chapters, sūtras, or pages assigned",
  "why": "Why this passage, why this week. What to look for, what tension it activates, what the YTT application is. 3–5 sentences minimum.",
  "module_reference": "Module X, Week N",
  "cross_refs": ["S2-W1-LISTEN-companion-item-id"]
},
```

**Fields:**
- `source` — required for all READ entries
- `author`, `translator`, `edition` — include when helpful; omit for YTT manual items where only `source` and `passage` are needed
- `passage` — always include; be specific (chapter numbers, sūtra numbers, page ranges)
- `why` — the most important field; this is the student-facing orientation
- `module_reference` — which module and week this belongs to (e.g. `"Module B, Week 3"`)
- `cross_refs` — array of companion item IDs; omit the field entirely if empty

### LISTEN — lecture or video
```js
"S2-W1-LISTEN-speaker-slug": {
  "speaker": "Speaker full name",
  "talk_title": "Talk or video title",
  "source": "Platform or series name",
  "why": "What this talk covers, what to listen for, how it connects to the week's reading.",
  "module_reference": "Module X, Week N",
  "cross_refs": ["S2-W1-READ-companion-item-id"]
},
```

### WRITE — essay prompt
```js
"S2-W5-WRITE-essay-slug": {
  "prompt": "Full prompt text. Structure it with numbered sub-questions if the task has multiple parts. End with a directive that connects to the capstone thesis.",
  "thesis_connection": "One or two sentences explaining how this entry builds toward the capstone argument."
},
```

### RECORD — class recording tips
```js
"S2-W4-RECORD-module-focused-class-youtube": {
  "tips": [
    {
      "thread": "Frame",
      "content": "What framing or theme to use for this week's recorded class."
    },
    {
      "thread": "Module B (Madhyamaka)",
      "content": "How to bring this week's Madhyamaka material into the class."
    },
    {
      "thread": "Module C (Abhidharma)",
      "content": "How to bring this week's Abhidharma material into the class."
    },
    {
      "thread": "Module A (Dzogchen)",
      "content": "How to bring this week's Dzogchen material into the class."
    },
    {
      "thread": "Module D / Kashmir Shaivism",
      "content": "How to bring the YTT manual or Kṣemarāja material into the class."
    }
  ]
},
```

---

## Build Process for a New Semester

### Phase 1 — Plan (before touching the file)

1. Define the semester structure: number of weeks, module assignments, weekly themes.
2. Identify the four philosophical threads (or equivalent for the new semester's focus).
3. Map which texts/lectures land in which weeks for each module.
4. Identify the tension codes: the recurring philosophical flashpoints across the curriculum.
5. Draft all item IDs on paper or in a separate doc before editing the HTML — it's much easier to catch conflicts and naming inconsistencies before they're in the file.

### Phase 2 — Curriculum Data

1. Open `tracker_v2.html` in a text editor.
2. Find the `#semester-data` block (search for `semester-data`).
3. Replace the existing semester JSON with the new semester's JSON, or add a new semester block if the app supports multi-semester mode.
4. Build out weeks and items using the Item Templates above.
5. Test in a browser — all weeks should render with correct labels and type badges before adding any READINGS content.

### Phase 3 — READINGS Object (module by module)

Work module by module, not week by week. This keeps the `why` fields internally consistent and avoids context-switching between traditions.

**Recommended order:**
1. Module C (Abhidharma) — establishes the taxonomic baseline other modules respond to
2. Lecture companion entries (Malcolm or equivalent) — written alongside Module C
3. Module B (Madhyamaka) — the analytical backbone
4. Module A (Dzogchen or equivalent contemplative thread) — the recognition thread
5. Module D (YTT manual + integration items) — largest block; do last
6. Video/platform entries (MyVinyasaPractice or equivalent) — one pass at the end

For each entry:
- Write the `why` field first; it drives everything else
- Add `cross_refs` after both companion items exist in the file
- Use consistent `module_reference` strings (e.g. always `"Module C, Week 5"` not `"Mod C Wk 5"`)

### Phase 4 — Quality Check

Run these greps before pushing:

```bash
# Confirm no placeholder IDs left
grep "YOUR_SUPABASE" tracker_v2.html

# Check all WRITE main prompts have READINGS entries
grep '"id": "S2-W.*-WRITE-' tracker_v2.html | grep -v 'self-reflections\|discussion-responses'
# Then check each ID appears as a key in READINGS:
grep '"S2-W.*-WRITE-' tracker_v2.html | grep -v '"id"'

# Check RECORD items W4–W11 all have READINGS entries
grep '"S2-W.*-RECORD-' tracker_v2.html | grep -v '"id"'
```

Open the file in a browser and click through every week, spot-checking ⓘ buttons to confirm modals render without JS errors.

### Phase 5 — Deploy

```bash
cd /path/to/ytt-curriculum-tracker

# Stage and commit
git add tracker_v2.html
git commit -m "Semester 2 full build"

# Push (requires a GitHub Classic PAT with repo scope embedded in the URL)
git remote set-url origin https://USERNAME:TOKEN@github.com/USERNAME/ytt-tracker.git
git push origin main
git remote set-url origin https://github.com/USERNAME/ytt-tracker.git  # strip token
```

GitHub Pages updates within ~5 minutes. Hard-reload (⌘⇧R) on the live URL to verify.

---

## Supabase (existing setup — no changes needed between semesters)

The Supabase credentials (`SUPABASE_URL`, `SUPABASE_KEY`, `USER_KEY`) are already in the file and don't need to change between semesters. State is stored as a single JSON blob per `USER_KEY` row, so new semester items simply appear in the tracked state automatically on first status change.

If you ever need to run multiple independent trackers (e.g. a student copy), change `USER_KEY` to a different unique string.

---

## Common Pitfalls

| Problem | Cause | Fix |
|---|---|---|
| ⓘ button dim on a WRITE or RECORD item | READINGS entry missing for that ID | Add the entry to the READINGS object |
| Modal opens blank | READINGS entry exists but has wrong key (ID mismatch) | Check the `"id"` in curriculum data matches the key in READINGS exactly |
| Cross-ref chip opens the wrong week | `cross_refs` array has a typo in the target ID | Grep for the target ID to confirm it exists |
| Label shows truncated text (e.g. "Three-doors vs") | `label` field was never completed | Fix the label string in the curriculum data |
| Push rejected (403) | Using fine-grained PAT instead of classic PAT, or wrong account | Generate a classic PAT (`ghp_...`) from the repo-owning account with `repo` scope |
| Push rejected (divergent histories) | Remote has an upload-only commit that doesn't share history with local | `git push origin main --force` |
