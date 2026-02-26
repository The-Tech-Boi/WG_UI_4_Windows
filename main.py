import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from wg_manager import WireGuardManager
import qrcode
from PIL import Image
import os
import io
import ctypes
import sys
import time

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WireGuard Manager for Windows")
        self.geometry("1100x600")
        
        # Set appearance
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        try:
            icon_p = resource_path("icon.ico")
            if os.path.exists(icon_p):
                self.iconbitmap(icon_p)
        except:
            pass

        if not is_admin():
            messagebox.showwarning("Admin Required", "This application requires Administrator privileges to manage WireGuard services and configurations. Some features may not work as expected.")

        self.manager = WireGuardManager()

        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="WG Manager", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.status_button = ctk.CTkButton(self.sidebar_frame, text="Status", command=self.show_status_view)
        self.status_button.grid(row=1, column=0, padx=20, pady=10)

        self.clients_button = ctk.CTkButton(self.sidebar_frame, text="Clients", command=self.show_clients_view)
        self.clients_button.grid(row=2, column=0, padx=20, pady=10)

        self.monitor_button = ctk.CTkButton(self.sidebar_frame, text="Monitor", command=self.show_monitor_view)
        self.monitor_button.grid(row=3, column=0, padx=20, pady=10)

        self.settings_button = ctk.CTkButton(self.sidebar_frame, text="Settings", command=self.show_settings_view)
        self.settings_button.grid(row=4, column=0, padx=20, pady=10)

        # Main Content Area
        self.main_content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(0, weight=1)

        self.show_status_view()

    def clear_view(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def show_status_view(self):
        self.clear_view()
        status = self.manager.get_service_status()
        
        title = ctk.CTkLabel(self.main_content, text="Service Status", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)

        color = "#2ecc71" if status == "Running" else "#e74c3c" if status == "Stopped" else "#95a5a6"
        status_label = ctk.CTkLabel(self.main_content, text=status, font=ctk.CTkFont(size=40), text_color=color)
        status_label.pack(pady=20)

        btn_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="Start", command=lambda: self.service_action("start"), fg_color="#27ae60").pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Stop", command=lambda: self.service_action("stop"), fg_color="#c0392b").pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Restart", command=lambda: self.service_action("restart")).pack(side="left", padx=10)

    def service_action(self, action):
        if self.manager.control_service(action):
            messagebox.showinfo("Success", f"Service {action}ed successfully.")
        else:
            messagebox.showerror("Error", f"Failed to {action} service. Make sure you are running as Admin.")
        self.show_status_view()

    def show_monitor_view(self):
        self.clear_view()
        
        top_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(top_frame, text="Live Monitor", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        right_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        right_frame.pack(side="right")
        
        if not hasattr(self, 'auto_refresh_var'):
            self.auto_refresh_var = ctk.BooleanVar(value=False)
            
        self.auto_refresh_switch = ctk.CTkSwitch(right_frame, text="Auto-Refresh (5s)", variable=self.auto_refresh_var, command=self.toggle_auto_refresh)
        self.auto_refresh_switch.pack(side="left", padx=(0, 10))

        ctk.CTkButton(right_frame, text="Refresh", command=self.refresh_monitor_data).pack(side="left")

        self.monitor_scrollable_frame = ctk.CTkScrollableFrame(self.main_content)
        self.monitor_scrollable_frame.pack(fill="both", expand=True)

        self.refresh_monitor_data()

    def toggle_auto_refresh(self):
        if self.auto_refresh_var.get():
            self.refresh_monitor_data()

    def refresh_monitor_data(self):
        if not hasattr(self, 'monitor_scrollable_frame') or not self.monitor_scrollable_frame.winfo_exists():
            return
            
        for widget in self.monitor_scrollable_frame.winfo_children():
            widget.destroy()

        dump_data = self.manager.get_wg_show_dump()
        if dump_data is None:
            ctk.CTkLabel(self.monitor_scrollable_frame, text="Could not retrieve WireGuard data.\nIs the service running and is WireGuard in your PATH?").pack(pady=20)
        elif not dump_data:
            ctk.CTkLabel(self.monitor_scrollable_frame, text="No active connections or peers found.").pack(pady=20)
        else:
            config_data = self.manager.parse_config()
            peers_conf = {p.get('PublicKey', ''): p.get('name', 'Unknown') for p in config_data['peers']}

            for peer in dump_data:
                pubkey = peer['public_key']
                name = peers_conf.get(pubkey, "Unknown Client")
                endpoint = peer['endpoint'] if peer['endpoint'] != '(none)' else 'Disconnected'
                handshake = peer['latest_handshake']
                rx = peer['transfer_rx']
                tx = peer['transfer_tx']

                # Format handshake
                if handshake == 0:
                    handshake_str = "Never"
                else:
                    diff = int(time.time()) - handshake
                    if diff < 60:
                        handshake_str = f"{diff} sec ago"
                    elif diff < 3600:
                        handshake_str = f"{diff // 60} min ago"
                    elif diff < 86400:
                        handshake_str = f"{diff // 3600} hr ago"
                    else:
                        handshake_str = f"{diff // 86400} days ago"

                # Format transfer
                def format_bytes(b):
                    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                        if b < 1024.0:
                            return f"{b:.2f} {unit}"
                        b /= 1024.0
                    return f"{b:.2f} PB"

                rx_str = format_bytes(rx)
                tx_str = format_bytes(tx)

                card = ctk.CTkFrame(self.monitor_scrollable_frame)
                card.pack(fill="x", pady=5, padx=5)

                # Row 1: Name and Endpoint
                row1 = ctk.CTkFrame(card, fg_color="transparent")
                row1.pack(fill="x", padx=10, pady=(10, 5))
                ctk.CTkLabel(row1, text=name, font=ctk.CTkFont(weight="bold", size=16)).pack(side="left")
                ctk.CTkLabel(row1, text=f"Endpoint: {endpoint}", text_color="gray").pack(side="right")

                # Row 2: Stats
                row2 = ctk.CTkFrame(card, fg_color="transparent")
                row2.pack(fill="x", padx=10, pady=(5, 10))
                ctk.CTkLabel(row2, text=f"Rx: {rx_str} | Tx: {tx_str}").pack(side="left")
                ctk.CTkLabel(row2, text=f"Handshake: {handshake_str}").pack(side="right")
                
                # pubkey truncated
                ctk.CTkLabel(row2, text=f" ({pubkey[:8]}...)", text_color="gray").pack(side="left", padx=5)

        if self.auto_refresh_var.get():
            self.monitor_scrollable_frame.after(5000, self.refresh_monitor_data)

    def show_clients_view(self):
        self.clear_view()
        data = self.manager.parse_config()
        
        top_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(top_frame, text="Connected Clients", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        ctk.CTkButton(top_frame, text="Add Client", command=self.add_client_dialog).pack(side="right")

        scrollable_frame = ctk.CTkScrollableFrame(self.main_content)
        scrollable_frame.pack(fill="both", expand=True)

        for peer in data['peers']:
            peer_frame = ctk.CTkFrame(scrollable_frame)
            peer_frame.pack(fill="x", pady=5, padx=5)
            
            name = peer.get('name', 'Unnamed')
            pubkey = peer.get('PublicKey', 'N/A')
            ips = peer.get('AllowedIPs', 'N/A')
            
            ctk.CTkLabel(peer_frame, text=f"{name}", font=ctk.CTkFont(weight="bold"), width=150).pack(side="left", padx=10)
            ctk.CTkLabel(peer_frame, text=f"{ips}", width=150).pack(side="left", padx=10)
            ctk.CTkLabel(peer_frame, text=f"{pubkey[:20]}...", width=200).pack(side="left", padx=10)
            
            ctk.CTkButton(peer_frame, text="QR", width=50, command=lambda p=peer: self.show_qr(p)).pack(side="right", padx=5)
            ctk.CTkButton(peer_frame, text="Edit", width=50, command=lambda p=peer: self.edit_client_dialog(p)).pack(side="right", padx=5)
            ctk.CTkButton(peer_frame, text="Delete", width=50, fg_color="#c0392b", command=lambda p=peer: self.delete_client(p)).pack(side="right", padx=5)

    def add_client_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Client")
        dialog.geometry("400x300")
        dialog.attributes("-topmost", True)

        ctk.CTkLabel(dialog, text="Client Name:").pack(pady=(20, 0))
        name_entry = ctk.CTkEntry(dialog, width=250)
        name_entry.pack(pady=5)

        ctk.CTkLabel(dialog, text="Allowed IP (e.g. 10.0.0.2/32):").pack(pady=(10, 0))
        ip_entry = ctk.CTkEntry(dialog, width=250)
        next_ip = self.manager.get_next_ip()
        ip_entry.insert(0, next_ip)
        ip_entry.pack(pady=5)

        def save():
            name = name_entry.get()
            ip = ip_entry.get()
            if not name:
                messagebox.showerror("Error", "Name is required")
                return
            
            priv, pub = self.manager.generate_keys()
            if not priv:
                messagebox.showerror("Error", "Could not generate keys. Check WG path.")
                return

            config_data = self.manager.parse_config()
            new_peer = {
                "name": name,
                "PublicKey": pub,
                "AllowedIPs": ip
            }
            config_data['peers'].append(new_peer)
            self.manager.write_config(config_data['interface'], config_data['peers'])
            
            # Show the private key info for client setup
            self.show_new_client_info(name, priv, ip, config_data['interface'])
            dialog.destroy()
            self.show_clients_view()

            # Prompt to restart service
            if messagebox.askyesno("Apply Changes", "Client added successfully. Would you like to restart the WireGuard service now to apply changes?"):
                self.service_action("restart")

        ctk.CTkButton(dialog, text="Generate & Save", command=save).pack(pady=20)

    def show_new_client_info(self, name, priv_key, ip, interface_data):
        info_win = ctk.CTkToplevel(self)
        info_win.title(f"Client Config: {name}")
        info_win.geometry("500x600")
        info_win.attributes("-topmost", True)

        server_pub_key = interface_data.get('PublicKey', '')
        if not server_pub_key and interface_data.get('PrivateKey'):
            server_pub_key = self.manager.get_public_key(interface_data.get('PrivateKey'))

        client_conf = f"[Interface]\nPrivateKey = {priv_key}\nAddress = {ip}\nDNS = 1.1.1.1\n\n[Peer]\nPublicKey = {server_pub_key}\nEndpoint = {self.manager.settings.get('endpoint', 'YOUR_SERVER_IP:51820')}\nAllowedIPs = 0.0.0.0/0"
        
        ctk.CTkLabel(info_win, text="Client Configuration", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        textbox = ctk.CTkTextbox(info_win, width=450, height=200)
        textbox.pack(pady=10)
        textbox.insert("0.0", client_conf)

        # QR Code
        qr = qrcode.QRCode(version=1, box_size=5, border=2)
        qr.add_data(client_conf)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert PIL image to Tkinter image
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        photo = Image.open(io.BytesIO(img_byte_arr))
        ctk_image = ctk.CTkImage(light_image=photo, dark_image=photo, size=(250, 250))
        
        qr_label = ctk.CTkLabel(info_win, text="", image=ctk_image)
        qr_label.pack(pady=10)

        def download_conf():
            try:
                desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
                filename = f"{name.replace(' ', '_')}.conf"
                filepath = os.path.join(desktop, filename)
                
                with open(filepath, 'w') as f:
                    f.write(client_conf)
                
                messagebox.showinfo("Success", f"Configuration saved to Desktop as {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {e}")

        ctk.CTkButton(info_win, text="Download Configuration (.conf)", command=download_conf, fg_color="#27ae60").pack(pady=10)

    def show_qr(self, peer):
        # This would need the private key which we don't store for security
        # But for this manager, we can provide a way to rebuild if known or just show public info
        messagebox.showinfo("Note", "Private keys are only shown during creation for security. QR codes for existing clients require their specific private key.")

    def delete_client(self, peer):
        if messagebox.askyesno("Confirm", f"Delete client {peer.get('name')}?"):
            config_data = self.manager.parse_config()
            config_data['peers'] = [p for p in config_data['peers'] if p.get('PublicKey') != peer.get('PublicKey')]
            self.manager.write_config(config_data['interface'], config_data['peers'])
            self.show_clients_view()

    def edit_client_dialog(self, peer):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Client")
        dialog.geometry("400x200")
        dialog.attributes("-topmost", True)

        ctk.CTkLabel(dialog, text="Client Name:").pack(pady=(20, 0))
        name_entry = ctk.CTkEntry(dialog, width=250)
        name_entry.insert(0, peer.get('name', ''))
        name_entry.pack(pady=5)

        def save():
            new_name = name_entry.get()
            if not new_name:
                messagebox.showerror("Error", "Name is required")
                return
            
            # Update name
            config_data = self.manager.parse_config()
            # Find the peer to update. We rely on PublicKey as unique ID.
            for p in config_data['peers']:
                if p.get('PublicKey') == peer.get('PublicKey'):
                    p['name'] = new_name
                    break
            
            self.manager.write_config(config_data['interface'], config_data['peers'])
            dialog.destroy()
            self.show_clients_view()
            
        ctk.CTkButton(dialog, text="Save", command=save).pack(pady=20)

    def show_settings_view(self):
        self.clear_view()
        
        ctk.CTkLabel(self.main_content, text="Settings", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        settings_frame = ctk.CTkFrame(self.main_content)
        settings_frame.pack(fill="x", padx=40, pady=20)

        # WG Path
        ctk.CTkLabel(settings_frame, text="WireGuard Path:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        wg_path_entry = ctk.CTkEntry(settings_frame, width=400)
        wg_path_entry.grid(row=0, column=1, padx=10, pady=10)
        wg_path_entry.insert(0, self.manager.settings.get("wg_path", ""))

        # Conf Path
        ctk.CTkLabel(settings_frame, text="Config Path:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        conf_path_entry = ctk.CTkEntry(settings_frame, width=400)
        conf_path_entry.grid(row=1, column=1, padx=10, pady=10)
        conf_path_entry.insert(0, self.manager.settings.get("conf_path", ""))

        # Endpoint
        ctk.CTkLabel(settings_frame, text="Server Endpoint:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        endpoint_entry = ctk.CTkEntry(settings_frame, width=400)
        endpoint_entry.grid(row=2, column=1, padx=10, pady=10)
        endpoint_entry.insert(0, self.manager.settings.get("endpoint", "YOUR_SERVER_IP:51820"))

        # Interface Name
        ctk.CTkLabel(settings_frame, text="Interface Name:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        interface_entry = ctk.CTkEntry(settings_frame, width=400)
        interface_entry.grid(row=3, column=1, padx=10, pady=10)
        interface_entry.insert(0, self.manager.settings.get("interface_name", "wg0"))

        def save_settings():
            new_settings = {
                "wg_path": wg_path_entry.get(),
                "conf_path": conf_path_entry.get(),
                "endpoint": endpoint_entry.get(),
                "interface_name": interface_entry.get()
            }
            self.manager.save_settings(new_settings)
            messagebox.showinfo("Success", "Settings saved.")

        ctk.CTkButton(self.main_content, text="Save Settings", command=save_settings).pack(pady=20)

if __name__ == "__main__":
    app = App()
    app.mainloop()
