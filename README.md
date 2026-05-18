# YTT Curriculum Thigle Map — Stage 1

A single-file interactive curriculum map for Semester 1 of the YTT integration curriculum.

## Opening the app

Double-click `thigle_map.html` in Finder to open it in your browser — no server or install required. If your browser blocks local JSON reads, serve it instead:

```
cd ytt-curriculum-tracker
python3 -m http.server 8080
```
Then open `http://localhost:8080/thigle_map.html`.

## Where your state lives

Progress is stored in your browser's `localStorage` under the key `ytt-tracker-state-v1`. This means:

- State survives browser restarts and page reloads automatically.
- **Clearing browser data will wipe your progress** — use the Export button before doing so.
- State is per-browser: switching to a different browser or device starts fresh.

Click the **↓ Export** button (top right) to download a timestamped JSON file (`ytt-tracker-state-YYYY-MM-DD.json`). Drop that file into your Drive folder for backup. To restore from a backup, paste its contents into the browser console: `localStorage.setItem('ytt-tracker-state-v1', JSON.stringify(<your JSON>)); location.reload()`.

## How to interact

- **Click a week node** — opens its items in the side panel. Click again to deselect.
- **Click an item** (satellite dot or panel row) — cycles status: not started → in progress → done.
- **Click a tension chip** (T1–T4, on ring or in panel) — highlights that tension's chord and the weeks that touch it.
- **Click the thigle center** or empty canvas — returns to semester summary.
- **Arrow keys ←/→** — step active week clockwise / counterclockwise.
- **Space** — mark the next incomplete item of the active week in-progress.
- **Escape** — deselect, return to summary.

The **streak counter** increments each calendar day you mark at least one item in-progress or done. It resets if you miss a day.

## Rebuilding after editing the curriculum

If you edit `Semester_1_Quick_Reference.md`, regenerate the embedded data:

```
python3 build.py Semester_1_Quick_Reference.md semester1.json
```

Then run the embed step to update `thigle_map.html` with the new JSON:

```python
import json, pathlib, re

json_data = json.load(open('semester1.json'))
html = pathlib.Path('thigle_map.html').read_text()
new_json = json.dumps(json_data, ensure_ascii=False, indent=2)
html = re.sub(
    r'(<script type="application/json" id="semester-data">\n).*?(\n</script>)',
    rf'\g<1>{new_json}\g<2>',
    html, flags=re.DOTALL
)
pathlib.Path('thigle_map.html').write_text(html)
print("Done — reload thigle_map.html in your browser.")
```

Alternatively, hand-edit the JSON block directly in `thigle_map.html` between the `<script type="application/json" id="semester-data">` tags.
