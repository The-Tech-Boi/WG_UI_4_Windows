import os
import subprocess
import sys
import customtkinter

def build():
    # Get customtkinter directory
    ctk_path = os.path.dirname(customtkinter.__file__)
    
    print(f"CustomTkinter path: {ctk_path}")
    
    # Construct PyInstaller command
    # --noconsole: hide terminal
    # --onefile: single executable
    # --add-data: include customtkinter files (needed for themes/etc)
    # --uac-admin: request admin privileges on windows
    # --name: output name
    
    cmd = [
        "pyinstaller",
        "--noconsole",
        "--onefile",
        f"--add-data={ctk_path};customtkinter",
        "--uac-admin",
        "--name=WireGuardManager",
        "--clean", # Clean cache before building
        "main.py"
    ]
    
    print("Running command:", " ".join(cmd))
    
    try:
        subprocess.run(cmd, check=True)
        print("\nBuild successful! Look in the 'dist' folder for WireGuardManager.exe")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed: {e}")
    except FileNotFoundError:
        print("\nError: PyInstaller not found. Please run 'pip install pyinstaller' first.")

if __name__ == "__main__":
    build()
