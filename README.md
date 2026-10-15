# Page Archiver Watcher

A Windows desktop tool that watches a Chromium-based browser window, detects newly opened
tabs / navigation, and archives the page content (HTML + URL record) for whitelisted domains.

## What it does

- Monitors browser top-level windows (via Win32 window enumeration) and recognizes new tabs.
- For pages on the whitelist (`tiktok.com`, `douyin.com`), it captures the rendered page and
  records the URL into `archived_urls.json`.
- Provides a Tkinter control panel to start / stop monitoring, view status, and manage archives.

## Layout

```
config.py           # archive dir, timeouts, whitelist domains
gui.py              # Tkinter GUI + browser-window detection
main.py             # entry point
page_archiver.py    # page capture / save logic
background.js       # browser-side capture helper (used by the extension side)
popup/              # extension popup UI
icons/              # UI assets
requirements.txt
run.bat             # one-click launcher
```

## Privacy note

Real browsing data is **not** committed to this repository:

- The `archived_pages/` directory (captured user pages) is excluded.
- `archived_urls.json` ships as an empty array `[]` - no real URLs are stored.

## Run

```
pip install -r requirements.txt
python main.py
```

Requires Windows and an Administrator shell (the window-monitoring / browser integration
needs elevated rights). Browser paths are configured in `gui.py` for a local install;
adjust them to your own environment.
