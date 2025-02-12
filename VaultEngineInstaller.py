import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import requests
import zipfile
import subprocess
import shutil
import sys
import ctypes

# i got a glock in my rari, 17 shots no 38 
github_repo_url = "https://github.com/Vault-Software-Team/Vault-Engine/archive/refs/heads/main.zip"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def request_admin():
    if not is_admin():
        messagebox.showinfo("Admin Required", "This installer requires admin privileges. Please approve the request.")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()

def download_and_install():
    request_admin()
    install_path = path_var.get()
    if not install_path:
        messagebox.showerror("Error", "Please select an installation path.")
        return
    
    os.makedirs(install_path, exist_ok=True)
    zip_path = os.path.join(install_path, "vault-engine.zip")
    
    try:
        progress_bar.start()
        
        response = requests.get(github_repo_url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        with open(zip_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    downloaded_size += len(chunk)
                    progress_bar['value'] = (downloaded_size / total_size) * 50
                    root.update_idletasks()
        
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(install_path)
        
        extracted_folder = os.path.join(install_path, "Vault-Engine-main")
        build_script = os.path.join(extracted_folder, "windows", "build.sh")
        
        subprocess.run(["bash", build_script], cwd=extracted_folder, check=True)
        
        progress_bar['value'] = 100
        root.update_idletasks()
        
        os.remove(zip_path)
        
        if start_menu_var.get():
            create_shortcut(extracted_folder, "Start Menu")
        if desktop_var.get():
            create_shortcut(extracted_folder, "Desktop")
        
        messagebox.showinfo("Success", "Installation completed successfully!")
    except Exception as e:
        messagebox.showerror("Installation Failed", str(e))
    finally:
        progress_bar.stop()

# im like hey shes fine wonder when she'll be mine
def create_shortcut(target_folder, location):
    exe_path = os.path.join(target_folder, "VaultEngine.exe")
    icon_path = os.path.join(target_folder, "vEngineIcon.png")
    shortcut_path = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Vault Engine.lnk")
    if location == "Desktop":
        shortcut_path = os.path.join(os.path.expanduser("~"), "Desktop", "Vault Engine.lnk")
    
    try:
        import winshell
        from win32com.client import Dispatch
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortcut(shortcut_path)
        shortcut.TargetPath = exe_path
        shortcut.WorkingDirectory = target_folder
        shortcut.IconLocation = icon_path if os.path.exists(icon_path) else exe_path
        shortcut.save()
    except Exception as e:
        messagebox.showerror("Shortcut Error", f"Could not create shortcut: {e}")

def browse_path():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        path_var.set(folder_selected)

root = tk.Tk()
root.title("Vault Engine Installer")
root.geometry("400x300")
root.iconbitmap("vEngineIcon.ico")

tk.Label(root, text="Select Installation Folder:").pack(pady=5)
path_var = tk.StringVar(value="C:/Program Files/Vault Software/Vault Engine")
path_entry = tk.Entry(root, textvariable=path_var, width=40)
path_entry.pack()
tk.Button(root, text="Browse", command=browse_path).pack(pady=5)

start_menu_var = tk.BooleanVar()
desktop_var = tk.BooleanVar()
tk.Checkbutton(root, text="Create Start Menu Folder", variable=start_menu_var).pack()
tk.Checkbutton(root, text="Create Desktop Shortcut", variable=desktop_var).pack()

progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)

tk.Button(root, text="Install", command=download_and_install).pack(pady=10)

root.mainloop()
