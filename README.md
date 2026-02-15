# WireGuard Manager for Windows

**⚠️ IMPORTANT NOTICE**: This application is a **GUI Wrapper** for an existing WireGuard installation. It is NOT a standalone WireGuard implementation. It requires the official WireGuard for Windows client to be installed on your system.

## 🔴 Crucial Limitation (DPAPI)
This application can only manage tunnels that were **deployed via the Command Line (CLI)** or created within this manager. 

**Why?** 
When you create a tunnel using the official WireGuard GUI, Windows encrypts the configuration file using **DPAPI (Data Protection API)** linked to the specific user account. This prevents other applications (like this manager) from reading or modifying the `.conf` file. 

To use this manager effectively, ensure your tunnels are placed in the configurations folder manually or created through this interface.

## Features
- **Modern UI**: Built with `customtkinter` for a native Windows feel.
- **Service Control**: Start, Stop, and Restart WireGuard services directly from the app.
- **Client Management**: Easily add and delete clients.
- **QR Code & Download**: Generate QR codes and download `.conf` files for new clients directly to your Desktop.
- **Configurable**: Change WireGuard installation, configuration paths, and interface names (e.g., `Async_Network`) via Settings.
- **Comments Support**: Client names are stored as comments in the configuration file to keep things organized.

## Requirements
- Windows (Tested on Windows Server/Windows 10/11)
- **Official WireGuard installed** on the system.
- Python 3.x (if running from source).
- **Administrator Privileges** (Required to control services and modify protected config files).

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
- `Config Path`: Points to your server's `.conf` file.
- `Interface Name`: Matches the name of your tunnel (e.g., `wg0` or `Async_Network`).
- `Server Endpoint`: Set to your public IP/Domain and port (e.g., `vpn.example.com:51820`).

## Building Standalone EXE
To create a single `.exe` file for distribution:
1. Run the build script:
   ```bash
   python build_exe.py
   ```
The resulting executable will be in the `dist/` folder. It will automatically request Administrator privileges when run.

## Open Source
This project is designed to be flexible. All paths are configurable, making it suitable for any environment.
