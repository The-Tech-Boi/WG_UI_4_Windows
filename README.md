# WireGuard Manager for Windows

A modern, Python-based GUI for managing WireGuard on Windows Server.

## Features
- **Modern UI**: Built with `customtkinter` for a native Windows feel.
- **Service Control**: Start, Stop, and Restart WireGuard services directly from the app.
- **Client Management**: Easily add and delete clients.
- **QR Code Generation**: Automatically generate QR codes and configuration files for new clients.
- **Configurable**: Change WireGuard installation and configuration paths via the Settings tab (perfect for non-standard installs).
- **Comments Support**: Client names are stored as comments in the `wg0.conf` file to keep things organized.

## Requirements
- Windows (Tested on Windows Server/Windows 10/11)
- Python 3.x
- WireGuard installed on the system
- **Administrator Privileges** (Required to control services and modify protected config files)

## Installation
1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python main.py
   ```

## Configuration
Upon first run, check the **Settings** tab to ensure:
- `WireGuard Path`: Points to your `wireguard.exe`.
- `Config Path`: Points to your `wg0.conf`.
- `Server Endpoint`: Set to your public IP/Domain and port (e.g., `vpn.example.com:51820`).

## Building Standalone EXE
To create a single `.exe` file for distribution:
1. Install build requirements:
   ```bash
   pip install pyinstaller
   ```
2. Run the build script:
   ```bash
   python build_exe.py
   ```
The resulting executable will be in the `dist/` folder. It will automatically request Administrator privileges when run.

## Open Source
This project is designed to be flexible. All paths are configurable, making it suitable for any environment.
