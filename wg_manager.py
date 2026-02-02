import os
import json
import subprocess
import re
import shutil
import time

class WireGuardManager:
    def __init__(self, app_name="WireGuardManager"):
        self.app_name = app_name
        self.app_data_dir = os.path.join(os.getenv('LOCALAPPDATA'), self.app_name)
        self.settings_path = os.path.join(self.app_data_dir, "settings.json")
        self.legacy_settings_path = "settings.json"
        
        # Ensure AppData directory exists
        if not os.path.exists(self.app_data_dir):
            os.makedirs(self.app_data_dir)
            
        # Migrate if needed
        self.migrate_settings()
        
        self.settings = self.load_settings()
        
    def migrate_settings(self):
        # If legacy file exists but new one doesn't, migrate
        if os.path.exists(self.legacy_settings_path) and not os.path.exists(self.settings_path):
            try:
                shutil.copy2(self.legacy_settings_path, self.settings_path)
                print(f"Migrated settings from {self.legacy_settings_path} to {self.settings_path}")
                # We leave the legacy file there for safety, but app uses the new one
            except Exception as e:
                print(f"Migration error: {e}")

    def load_settings(self):
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "wg_path": "C:\\Program Files\\WireGuard\\wireguard.exe",
            "conf_path": "C:\\Program Files\\WireGuard\\Data\\Configurations\\wg0.conf",
            "interface_name": "wg0",
            "endpoint": "YOUR_SERVER_IP:51820"
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
        
        # To preserve formatting, we'll read the existing file
        # and only append new peers if they don't exist.
        # For simplicity and to ensure '# Name:' comments are handled,
        # we will rebuild the config but try to be cleaner.
        
        lines = ["[Interface]"]
        if 'PrivateKey' in interface_data:
            lines.append(f"PrivateKey = {interface_data['PrivateKey']}")
        if 'Address' in interface_data:
            lines.append(f"Address = {interface_data['Address']}")
        if 'ListenPort' in interface_data:
            lines.append(f"ListenPort = {interface_data['ListenPort']}")
        if 'DNS' in interface_data:
            lines.append(f"DNS = {interface_data['DNS']}")
        
        # Add any other keys from interface_data
        known_keys = ['PrivateKey', 'Address', 'ListenPort', 'DNS', 'name']
        for k, v in interface_data.items():
            if k not in known_keys:
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
            # shell=False is safer
            priv_key = subprocess.check_output([wg_exe, "genkey"], shell=False).decode().strip()
            pub_key = subprocess.check_output([wg_exe, "pubkey"], input=priv_key.encode(), shell=False).decode().strip()
            return priv_key, pub_key
        except Exception as e:
            print(f"Error generating keys: {e}")
            return None, None

    def get_public_key(self, private_key):
        wg_exe = self.settings.get("wg_path").replace("wireguard.exe", "wg.exe")
        if not os.path.exists(wg_exe):
             wg_exe = os.path.join(os.path.dirname(self.settings.get("wg_path")), "wg.exe")
        
        try:
            pub_key = subprocess.check_output([wg_exe, "pubkey"], input=private_key.encode(), shell=False).decode().strip()
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
            output = subprocess.check_output(["sc", "query", service_name], shell=False).decode()
            if "RUNNING" in output:
                return "Running"
            if "STOPPED" in output:
                return "Stopped"
            return "Unknown"
        except:
            return "Not Installed"

    def get_next_ip(self):
        config = self.parse_config()
        used_ips = []
        
        # Check interface IP
        if 'Address' in config['interface']:
            addr = config['interface']['Address'].split(',')[0].strip().split('/')[0]
            try:
                parts = list(map(int, addr.split('.')))
                if len(parts) == 4:
                    used_ips.append(parts)
            except:
                pass
                
        # Check peers
        for peer in config['peers']:
            allowed_ips = peer.get('AllowedIPs', '')
            if allowed_ips:
                first_ip = allowed_ips.split(',')[0].strip().split('/')[0]
                try:
                    parts = list(map(int, first_ip.split('.')))
                    if len(parts) == 4:
                        used_ips.append(parts)
                except:
                    pass
        
        if not used_ips:
            return "10.0.0.2/32"
            
        # Sort and find max
        used_ips.sort()
        last_ip = used_ips[-1]
        
        # Simple increment of 4th octet
        # (Real implementation handles subnet overflow, but this covers 99% of basic WG setups)
        next_val = last_ip[3] + 1
        
        return f"{last_ip[0]}.{last_ip[1]}.{last_ip[2]}.{next_val}/32"
