# tracker_v2.html — Setup Guide

## What this gives you

`tracker_v2.html` is a self-contained single-file app. Out of the box it works exactly like the original `thigle_map.html` — state lives in `localStorage` and the sync badge shows **Local**. Once you complete the steps below, every status change is also written to Supabase (cloud backup, device sync), and the badge shows **Synced**.

---

## Step 1 — Create a Supabase project

1. Go to [supabase.com](https://supabase.com) and sign in (free tier is fine).
2. Click **New project**. Choose a name (e.g. `ytt-tracker`), set a database password, pick the closest region.
3. Wait ~2 minutes for provisioning.

---

## Step 2 — Create the table

In your project's **SQL Editor**, run:

```sql
create table tracker_state (
  user_key    text primary key,
  state       jsonb not null,
  updated_at  timestamptz not null default now()
);

-- Enable Row Level Security
alter table tracker_state enable row level security;

-- Allow anon key full access (single-user app — no auth needed)
create policy "anon full access"
  on tracker_state
  for all
  to anon
  using (true)
  with check (true);
```

Click **Run**. You should see `Success. No rows returned.`

---

## Step 3 — Get your credentials

In the Supabase sidebar: **Settings → API**.

You need two values:

| What | Where | Looks like |
|---|---|---|
| **Project URL** | "Project URL" box | `https://xyzxyz.supabase.co` |
| **Anon key** | "Project API keys → anon public" | `eyJhbGci…` (long JWT) |

Copy both.

---

## Step 4 — Paste credentials into tracker_v2.html

Open `tracker_v2.html` in any text editor. Near the top of the `<script>` block (around line 1625) you'll see:

```js
const SUPABASE_URL = 'YOUR_SUPABASE_PROJECT_URL';
const SUPABASE_KEY = 'YOUR_SUPABASE_ANON_KEY';
const USER_KEY     = 'noah-s1-a7f3b9';
```

Replace the two placeholder strings with your actual values. `USER_KEY` is a string you invent — it's just the row identifier in the database. The default is fine; change it only if you want to run multiple independent trackers.

---

## Step 5 — Migrate existing localStorage state (optional)

If you've already been using `thigle_map.html` and want to carry your progress over:

1. Open `thigle_map.html` in a browser.
2. Click the **Export** button — this downloads `ytt-tracker-state-YYYY-MM-DD.json`.
3. Open `tracker_v2.html` in a browser (before adding credentials).
4. Open the browser console (⌥⌘J / F12 → Console) and run:

```js
const state = /* paste the full JSON here as an object literal */;
localStorage.setItem('ytt-tracker-state-v1', JSON.stringify(state));
location.reload();
```

Alternatively, paste the file contents from the JSON export directly. After reload you'll see your existing progress. Once you add the Supabase credentials and reload again, it will sync to the cloud automatically on the next status change.

---

## Step 6 — Verify sync is working

1. Open `tracker_v2.html` in a browser. The sync badge in the top-right should show **Synced** (green dot). If it still shows **Local**, double-check you replaced both placeholder strings and saved the file.
2. Click any week node, then click an item's status circle to cycle it. The badge should briefly show **Saving…** then return to **Synced**.
3. In Supabase → **Table Editor → tracker_state**, you should see one row with your `USER_KEY` and a `state` JSON object.

---

## Hosting on Squarespace

Squarespace does not serve raw `.html` files as pages, but you can embed the entire app in a Code Block:

1. In Squarespace editor, add a **Code Block** to any page.
2. Open `tracker_v2.html` in a text editor.
3. Copy **everything from `<style>` through the closing `</script>`** (i.e. the full content between `<head>` and `</html>`, excluding the outer `<html>/<head>/<body>` wrappers since Squarespace provides those).
4. Paste into the Code Block. Make sure **HTML** mode is selected (not Markdown).
5. Publish the page. The app renders inline.

**Important**: Squarespace wraps your code in its own page DOM, so the `height: 100%` layout will not fill the full viewport the way it does in a standalone file. To fix this, add the following at the top of the pasted code:

```html
<style>
  #app { height: 80vh; min-height: 520px; }
  body, html { height: auto !important; overflow: auto !important; }
</style>
```

Alternatively, host `tracker_v2.html` on any static host (GitHub Pages, Netlify, Cloudflare Pages — all free) and embed it in Squarespace via an `<iframe>`:

```html
<iframe src="https://YOUR-HOST/tracker_v2.html"
        style="width:100%;height:85vh;border:none;border-radius:12px;">
</iframe>
```

The iframe approach preserves the full-viewport layout and is generally easier to maintain.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Badge stays **Local** after adding credentials | Placeholder string still present, or file not saved | Check for trailing spaces in the URL/key strings |
| Supabase returns 401 | Anon key pasted incorrectly | Re-copy from Settings → API; make sure you used the **anon** key, not the **service role** key |
| State doesn't persist across devices | `USER_KEY` differs between devices | Make sure both copies of the file have the identical `USER_KEY` string |
| Supabase returns 42501 (permission denied) | RLS policy not created | Re-run the SQL from Step 2 |
| Cross-ref chips open wrong week | Item exists in Weeks 5–14 (detail not yet populated) | Expected — READINGS covers Weeks 1–4 only in this version |
