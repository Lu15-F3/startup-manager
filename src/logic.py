#!/usr/bin/env python3
import os
import glob
import json

# Definição de caminhos profissionais seguindo o padrão XDG
CONFIG_DIR = os.path.expanduser("~/.config/startup_manager")
AUTOSTART_DIR = os.path.expanduser("~/.config/autostart")
BIN_DIR = os.path.expanduser("~/.local/bin")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
SCRIPT_PATH = os.path.join(BIN_DIR, "startup-launcher.sh")
DESKTOP_ENTRY = os.path.join(AUTOSTART_DIR, "startup_manager_script.desktop")

def get_installed_apps():
    """
    Varre as pastas do Fedora em busca de arquivos .desktop e categoriza por origem.
    """
    path_map = {
        "/usr/share/applications": "Sistema (RPM)",
        "/var/lib/flatpak/exports/share/applications": "Flatpak",
        os.path.expanduser("~/.local/share/applications"): "Usuário/AppImage"
    }
    
    apps_found = []

    for path, category in path_map.items():
        if not os.path.exists(path):
            continue
            
        for desktop_file in glob.glob(os.path.join(path, "*.desktop")):
            try:
                with open(desktop_file, 'r', encoding='utf-8') as f:
                    app_info = {"name": "", "exec": "", "category": category}
                    for line in f:
                        if line.startswith("Name="):
                            app_info["name"] = line.replace("Name=", "").strip()
                        elif line.startswith("Exec="):
                            # Limpa o comando de argumentos como %u ou %f
                            command = line.replace("Exec=", "").split('%')[0].strip()
                            app_info["exec"] = command
                        
                    if app_info["name"] and app_info["exec"]:
                        apps_found.append(app_info)
            except Exception:
                continue

    # Remove duplicatas mantendo a primeira ocorrência encontrada
    unique_apps = {}
    for app in apps_found:
        if app['name'] not in unique_apps:
            unique_apps[app['name']] = app
            
    return sorted(unique_apps.values(), key=lambda x: (x['category'], x['name']))

def generate_startup_script(app_list):
    """
    Cria o script bash em ~/.local/bin/ e aplica permissão de execução.
    app_list agora espera uma lista de tuplas: (comando, delay, argumentos)
    """
    if not os.path.exists(BIN_DIR):
        os.makedirs(BIN_DIR)
    
    content = "#!/bin/bash\n\n# Gerado via Startup Manager\n\n"
    for cmd, delay, args in app_list:
        if delay > 0:
            content += f"sleep {delay}\n"
        
        # Monta o comando com argumentos, se existirem
        full_command = f"{cmd} {args}".strip()
        content += f"{full_command} &\n\n"
    
    try:
        with open(SCRIPT_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        os.chmod(SCRIPT_PATH, 0o755) # Permissão +x
        return SCRIPT_PATH
    except Exception as e:
        print(f"Erro ao gerar script: {e}")
        return None

def save_config(selected_apps):
    """
    Salva a fila atual em ~/.config/startup_manager/config.json
    """
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
        
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(selected_apps, f, indent=4)
        return True
    except Exception as e:
        print(f"Erro ao salvar config: {e}")
        return False

def load_config():
    """
    Carrega as configurações salvas. Retorna lista vazia se falhar ou não existir.
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except (json.JSONDecodeError, Exception):
            return []
    return []

def enable_autostart(script_path):
    """
    Cria a entrada de autostart no KDE Plasma para disparar o script no login.
    """
    if not os.path.exists(AUTOSTART_DIR):
        os.makedirs(AUTOSTART_DIR)
        
    content = f"""[Desktop Entry]
Type=Application
Exec={script_path}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Startup Manager Script
Comment=Inicia aplicativos com atraso personalizado
"""
    try:
        with open(DESKTOP_ENTRY, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Erro ao ativar autostart: {e}")
        return False

def uninstall_everything():
    """
    Remove todos os arquivos e vestígios criados pelo aplicativo.
    """
    files_to_remove = [SCRIPT_PATH, CONFIG_FILE, DESKTOP_ENTRY]
    
    for file in files_to_remove:
        if os.path.exists(file):
            try:
                os.remove(file)
            except Exception as e:
                print(f"Erro ao remover {file}: {e}")
    
    # Remove a pasta de configuração se estiver vazia
    if os.path.exists(CONFIG_DIR) and not os.listdir(CONFIG_DIR):
        os.rmdir(CONFIG_DIR)
    
    return True