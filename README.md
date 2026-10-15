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

Captured HTML pages, browsing URL history, and local browser configuration are runtime data and are not tracked by Git. The repository's `.gitignore` excludes `archived_pages/`, `archived_urls.json`, and `gui_config.json`. If the app is run again, these files may be recreated locally; do not force-add them to a public commit.

## Browser path configuration

The browser executable and user-data directory are no longer hard-coded to one machine. Defaults are derived from `ProgramFiles(x86)` and `LOCALAPPDATA`. Set these environment variables before first launch if your installation differs:

- `ZHANFU_BROWSER_PATH`: full path to the browser executable
- `ZHANFU_USER_DATA_DIR`: browser user-data directory (use only a profile you are authorized to access)

If a local `gui_config.json` already exists, its `browser_path` and `user_data` values take precedence over defaults. Keep this local config out of version control.

## Run

```powershell
python -m pip install -r requirements.txt
python main.py
```

Requires Windows; some window-monitoring operations may need elevated rights. Review the target browser path and permissions before starting.

## License & Attribution / 许可与来源

Original project code authored for this repository is released under the MIT License; see [LICENSE](./LICENSE).

When reusing or redistributing a substantial portion, retain the LICENSE and its copyright notice. The copyright notice includes this original source URL: https://github.com/change979666/page-archiver-watcher. Please keep the source link visible in your redistributed source or project documentation.

This license applies only to original material that the repository maintainer has the right to license. Third-party libraries, vendor code, platform SDKs, trademarks, screenshots, icons, fonts, and other external assets remain subject to their respective licenses and terms. Review those terms before reuse.

**Project status:** personal/archived project, shared as-is. Maintenance, compatibility, and production readiness are not guaranteed.
