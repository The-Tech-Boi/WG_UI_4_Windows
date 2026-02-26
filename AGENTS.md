# AGENTS.md

## Project Context
- **Goal**: Create a standalone .exe using PyInstaller.
- **Current Status**: Maintenance and Reliability phase completed. Settings moved to AppData, config parser improved, restart prompt added. MIT License added and synced to GitHub.
- **Tech**: CustomTkinter, Python, WG CLI.
- **Requirement**: Make WireGuard path and config path configurable (Open Source friendly).
- **Current Status**: Project structure initialized, requirements and settings created.
- **Current Status**: auto-increment IP and Edit Client Name implemented. Ready for build.
- **Next Steps**: Implement UI Customization phase based on the "Modern Glass" theme (see [THEME.md](file:///c:/Users/Async/Desktop/WG_UI_4_Windows/docs/THEME.md)).
- **Next Steps**: Implement Email-OTP via M365 (Microsoft Graph API) and System Tray support using `pystray`.
- **Security**: Adding a "Gatekeeper" API with an allow-list for employee emails.
- **Current Status**: UI Theme specification created in `docs/THEME.md`.
- **Planned**: Researching WireGuard embedding (wireguard-nt) for true standalone functionality.
- **Current Status**: Added "Interface Name" setting to support existing GUI installations; Rebuilding.
- **Client Storage**: Peers/Clients are saved directly in the WireGuard `.conf` file. Names are preserved via `# Name: ` comments. Application configuration is in `%LOCALAPPDATA%\WireGuardManager\settings.json`.
- **Current Status**: Implemented "Live Monitor" feature. It parses `wg show <interface> dump` to track realtime statistics (Rx/Tx, handshake time, endpoints) and maps IP/Public Keys back to Usernames. Also generated and applied a custom app icon.
- **Current Status**: Updated `build_exe.py` to include the new custom icon and started a fresh PyInstaller build for `dist/WireGuardManager.exe`.
- **Bug Fix**: Fixed "blue square" icon issue in bundled EXE by using `sys._MEIPASS` path resolution and correctly bundling `icon.ico` with `--add-data`. 
