# WG_UI_4_Windows — Latest Status & Issues Report (2026-02-01)

## What Happened (Latest)
- Git repository initialized.
- Code committed.
- Repository pushed to GitHub: `https://github.com/The-Tech-Boi/WG_UI_4_Windows.git`.

## What’s in the Repo Now (As Reported)
- `main.py`: CustomTkinter-based GUI (includes derived Public Key fix).
- `wg_manager.py`: Backend logic (includes 10-second wait loop for service restarts).
- `build_exe.py`: One-click packaging script for PyInstaller.
- `settings.json`: Configurable paths (defaults provided).
- `README.md`: Documentation including standalone/build sections.

## Issues Observed in Current Repo State

### 1) Build artifacts and binaries are committed
The repository currently tracks build output and caches (examples):
- `dist/WireGuardManager.exe`
- `build/WireGuardManager/*`
- `__pycache__/wg_manager.cpython-314.pyc`

Impact:
- Repo becomes very large and noisy (harder diffs, slower clones, larger PRs).
- Build outputs are machine/environment-specific and frequently change.
- Shipping the `.exe` via git history is usually the wrong distribution channel (prefer Releases/artifacts).

### 2) No `.gitignore`
No `.gitignore` is present.

Impact:
- High risk of accidentally committing build output, caches, temporary files, and local settings.

### 3) Non-portable PyInstaller spec file
`WireGuardManager.spec` contains machine-specific absolute paths for `customtkinter` in `datas=[(...)]`.

Impact:
- Builds may fail or require manual edits on other machines and CI environments.

### 4) Settings file location tied to current working directory
`WireGuardManager(settings_path="settings.json")` uses a relative settings path (current working directory).

Impact:
- In a packaged `--onefile` EXE, the working directory may be unpredictable and/or not writable.
- Settings may fail to save or appear to “reset” depending on how/where the EXE is launched.

### 5) Endpoint setting is partially integrated
The UI saves an `endpoint` value, but the default settings structure does not include `endpoint`.

Impact:
- Client config generation can fall back to placeholders or unexpected values when settings are missing.

### 6) Config parsing/writing is not round-trip safe
The config is parsed and then rewritten from scratch, which can drop or change:
- ordering/formatting,
- non-`# Name:` comments,
- duplicated keys (e.g., multiple `DNS` / `Address` lines),
- any non-standard directives not anticipated by the parser.

Impact:
- Risk of config corruption or subtle behavior changes in `wg0.conf`.

### 7) Subprocess usage is fragile (`shell=True`)
`shell=True` is used for some `subprocess.check_output()` calls.

Impact:
- Avoidable quoting/behavior edge cases and harder-to-debug failures.

### 8) Changes don’t necessarily apply to the running tunnel automatically
After adding/deleting clients, the config file is updated, but the tunnel isn’t necessarily restarted/applied.

Impact:
- Users expect the change to take effect immediately but may need a manual restart.

## Recommendations (Priority Order)
1) Add a `.gitignore` and stop tracking build output/caches:
   - Remove `build/`, `dist/`, and `__pycache__/` from git tracking.
   - Keep build products out of history; publish the EXE via GitHub Releases instead.
2) Make builds reproducible:
   - Remove machine-specific absolute paths from `WireGuardManager.spec`, or document/standardize on `build_exe.py` as the single supported build method.
3) Move settings to a stable per-user location:
   - Use `%LOCALAPPDATA%\\WireGuardManager\\settings.json` (or similar), and migrate from a legacy `settings.json` in CWD if present.
4) Make config edits safer:
   - Preserve existing formatting/content as much as possible; avoid rewriting the entire config unless you fully support all directives you might encounter.
5) Improve reliability and UX:
   - Remove `shell=True` where not needed and surface errors in the UI (since the EXE runs `--noconsole`).
   - Prompt to restart/apply changes after modifications (or add an “auto-restart after changes” toggle).

