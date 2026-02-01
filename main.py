import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from wg_manager import WireGuardManager
import qrcode
from PIL import Image
import os
import io
import ctypes

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

        self.settings_button = ctk.CTkButton(self.sidebar_frame, text="Settings", command=self.show_settings_view)
        self.settings_button.grid(row=3, column=0, padx=20, pady=10)

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
        ip_entry.insert(0, "10.0.0.2/32")
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

        def save_settings():
            new_settings = {
                "wg_path": wg_path_entry.get(),
                "conf_path": conf_path_entry.get(),
                "endpoint": endpoint_entry.get(),
                "interface_name": self.manager.settings.get("interface_name", "wg0")
            }
            self.manager.save_settings(new_settings)
            messagebox.showinfo("Success", "Settings saved.")

        ctk.CTkButton(self.main_content, text="Save Settings", command=save_settings).pack(pady=20)

if __name__ == "__main__":
    app = App()
    app.mainloop()
