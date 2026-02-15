# Technical Specification: WireGuard OTP Gatekeeper

## 1. Project Overview
Secure remote access for office employees using WireGuard VPN with a custom Multi-Factor Authentication (MFA) layer. The system leverages existing Microsoft 365 (M365) accounts for OTP delivery via email.

## 2. System Architecture

### 2.1 Server-Side ("Gatekeeper" API)
- **Role**: Validates users, handles OTP lifecycle, and dynamically modifies WireGuard configuration.
- **Tech Stack**:
  - **FastAPI**: Lightweight asynchronous web framework.
  - **PyOTP**: For generating time-synced or counter-based 6-digit codes.
  - **MSAL (Microsoft Authentication Library)**: Authenticates the server to M365 Graph API.
  - **WireGuard CLI (`wg`)**: Used to activate/deactivate peers on the fly.
- **Key Logic**:
  - Maintains a `whitelist.json` of authorized employee emails.
  - Generates an OTP upon request from a whitelisted email.
  - Sends the OTP via M365 Graph API.
  - Upon successful verification, executes: `wg set wg0 peer <PublicKey> allowed-ips <IP>`.

### 2.2 Client-Side (WireGuard Manager)
- **Role**: Provides the user interface for employees to authenticate and connect.
- **Tech Stack**:
  - **CustomTkinter**: For a modern, high-DPI desktop UI.
  - **pystray**: Enables the application to run as a system tray icon.
  - **requests**: For communicating with the Gatekeeper API.
- **UI/UX Flow**:
  1. **Screen 1 (Email)**: User enters their office electronic mail.
  2. **Screen 2 (OTP)**: User enters the 6-digit code received.
  3. **System Tray Integration**: Minimized to tray on close; right-click menu for Quick Connect/Disconnect.

## 3. Security Requirements
- **Pre-Authentication**: Peers are *not* active in the WireGuard config until OTP verification succeeds.
- **Session Expiry**: Authenticated peers are automatically removed from the active config after a set duration (e.g., 8-12 hours).
- **Encryption**: Communication between Client and Gatekeeper API must be over HTTPS.
- **Whitelisting**: Only emails in the predefined list can trigger an OTP.

## 4. Deployment Model
- **Server**: Windows Server running the WireGuard service and the Gatekeeper API (as a Windows Service or via Docker).
- **Clients**: Windows workstations running a standalone `.exe` bundled with PyInstaller.

## 5. Development Milestones
1.  **Backend MVP**: API with whitelisting and MSAL email sending.
2.  **Peer Manager**: Logic to run `wg` commands and handle session timers.
3.  **UI Refactor**: Implement the 2-screen flow and `pystray` system tray object.
4.  **Packaging**: Bundle as a portable Windows executable.
