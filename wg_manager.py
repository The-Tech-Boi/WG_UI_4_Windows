import os
import json
import subprocess
import re
import shutil
import time

class WireGuardManager:
    def __init__(self, settings_path="settings.json"):
        self.settings_path = settings_path
        self.settings = self.load_settings()
        
    def load_settings(self):
        if os.path.exists(self.settings_path):
            with open(self.settings_path, 'r') as f:
                return json.load(f)
        return {
            "wg_path": "C:\\Program Files\\WireGuard\\wireguard.exe",
            "conf_path": "C:\\Program Files\\WireGuard\\Data\\Configurations\\wg0.conf",
            "interface_name": "wg0"
        }

    def save_settings(self, settings):
        self.settings = settings
        with open(self.settings_path, 'w') as f:
            json.dump(settings, f, indent=4)

    def get_config_content(self):
        conf_path = self.settings.get("conf_path")
        if os.path.exists(conf_path):
            with open(conf_path, 'r') as f:
                return f.read()
        return ""

    def parse_config(self):
        content = self.get_config_content()
        if not content:
            return {"interface": {}, "peers": []}

        # Split into sections
        sections = re.split(r'\[(Interface|Peer)\]', content, flags=re.IGNORECASE)
        
        interface_data = {}
        peers = []
        
        # The split returns [pre-text, 'Interface', content, 'Peer', content, ...]
        # We start from index 1
        for i in range(1, len(sections), 2):
            section_type = sections[i].lower()
            section_content = sections[i+1]
            
            data = {}
            # Extract comments for name
            name_match = re.search(r'#\s*Name:\s*(.*)', section_content)
            if name_match:
                data['name'] = name_match.group(1).strip()
            
            # Extract keys/values
            lines = section_content.strip().split('\n')
            for line in lines:
                if '=' in line:
                    key, val = line.split('=', 1)
                    data[key.strip()] = val.strip()
            
            if section_type == 'interface':
                interface_data = data
            else:
                peers.append(data)
                
        return {"interface": interface_data, "peers": peers}

    def write_config(self, interface_data, peers):
        conf_path = self.settings.get("conf_path")
        
        lines = ["[Interface]"]
        if 'name' in interface_data:
            lines.append(f"# Name: {interface_data['name']}")
        
        for k, v in interface_data.items():
            if k != 'name':
                lines.append(f"{k} = {v}")
        
        for peer in peers:
            lines.append("\n[Peer]")
            if 'name' in peer:
                lines.append(f"# Name: {peer['name']}")
            for k, v in peer.items():
                if k != 'name':
                    lines.append(f"{k} = {v}")
                    
        content = "\n".join(lines)
        
        # Backup before writing
        if os.path.exists(conf_path):
            shutil.copy2(conf_path, conf_path + ".bak")
            
        with open(conf_path, 'w') as f:
            f.write(content)

    def generate_keys(self):
        wg_exe = self.settings.get("wg_path").replace("wireguard.exe", "wg.exe")
        if not os.path.exists(wg_exe):
             wg_exe = os.path.join(os.path.dirname(self.settings.get("wg_path")), "wg.exe")

        try:
            priv_key = subprocess.check_output([wg_exe, "genkey"], shell=True).decode().strip()
            pub_key = subprocess.check_output([wg_exe, "pubkey"], input=priv_key.encode(), shell=True).decode().strip()
            return priv_key, pub_key
        except Exception as e:
            print(f"Error generating keys: {e}")
            return None, None

    def get_public_key(self, private_key):
        wg_exe = self.settings.get("wg_path").replace("wireguard.exe", "wg.exe")
        if not os.path.exists(wg_exe):
             wg_exe = os.path.join(os.path.dirname(self.settings.get("wg_path")), "wg.exe")
        
        try:
            pub_key = subprocess.check_output([wg_exe, "pubkey"], input=private_key.encode(), shell=True).decode().strip()
            return pub_key
        except Exception as e:
            print(f"Error deriving public key: {e}")
            return None

    def control_service(self, action):
        interface = self.settings.get("interface_name", "wg0")
        service_name = f"WireGuardTunnel${interface}"
        
        try:
            if action == "restart":
                # Stop the service
                subprocess.run(["sc", "stop", service_name], check=False, capture_output=True)
                
                # Wait for it to stop (max 10 seconds)
                for _ in range(10):
                    status = self.get_service_status()
                    if status == "Stopped":
                        break
                    time.sleep(1)
                
                # Start the service
                subprocess.run(["sc", "start", service_name], check=True, capture_output=True)
            else:
                subprocess.run(["sc", action, service_name], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            print(f"Service control error: {error_msg}")
            return False

    def get_service_status(self):
        interface = self.settings.get("interface_name", "wg0")
        service_name = f"WireGuardTunnel${interface}"
        try:
            output = subprocess.check_output(["sc", "query", service_name], shell=True).decode()
            if "RUNNING" in output:
                return "Running"
            if "STOPPED" in output:
                return "Stopped"
            return "Unknown"
        except:
            return "Not Installed"
