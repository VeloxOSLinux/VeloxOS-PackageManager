import subprocess
import os


def find_system_icon(name):
    """Versucht ein passendes Icon im System zu finden."""
    # Häufige Orte für Icons unter Linux
    icon_base_paths = [
        "/usr/share/icons/hicolor/48x48/apps",
        "/usr/share/icons/hicolor/64x64/apps",
        "/usr/share/icons/hicolor/scalable/apps",
        "/usr/share/pixmaps"
    ]

    # Suche nach exaktem Namen oder Namensbestandteilen
    search_names = [name, name.lower(), name.split('-')[0]]

    for base in icon_base_paths:
        if not os.path.exists(base):
            continue
        for s_name in search_names:
            for ext in [".png", ".svg", ".xpm"]:
                icon_path = os.path.join(base, s_name + ext)
                if os.path.exists(icon_path):
                    return icon_path
    return None


def get_installed_packages():
    """Liefert installierte Pakete mit Pfaden zu lokalen Icons."""
    packages = []

    # 1. --- Native Pakete (CachyOS / Repo) ---
    try:
        output = subprocess.check_output(["pacman", "-Qn"], text=True, stderr=subprocess.DEVNULL)
        for line in output.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                name, version = parts[0], parts[1]
                packages.append({
                    "name": name,
                    "source": "System",
                    "version": version,
                    "description": "System-Paket",
                    "icon_url": find_system_icon(name)  # Hier speichern wir den lokalen Pfad
                })
    except Exception:
        pass

    # 2. --- AUR Pakete ---
    try:
        output = subprocess.check_output(["pacman", "-Qm"], text=True, stderr=subprocess.DEVNULL)
        for line in output.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                name, version = parts[0], parts[1]
                packages.append({
                    "name": name,
                    "source": "AUR",
                    "version": version,
                    "description": "AUR-Paket",
                    "icon_url": find_system_icon(name)
                })
    except Exception:
        pass

    # 3. --- Flatpak Pakete ---
    try:
        output = subprocess.check_output(
            ["flatpak", "list", "--installed", "--columns=application,version,origin"],
            text=True, stderr=subprocess.DEVNULL
        )
        for line in output.splitlines():
            parts = line.split('\t')
            if len(parts) >= 3:
                app_id, version, origin = parts[0], parts[1], parts[2]
                # Bei Flatpak haben wir oft schon Icons im Cache oder nutzen die ID
                packages.append({
                    "name": app_id,
                    "source": "Flathub" if "flathub" in origin.lower() else "Flatpak",
                    "version": version,
                    "description": "Flatpak-App",
                    "icon_url": f"https://dl.flathub.org/repo/appstream/x86_64/icons/128x128/{app_id}.png"
                })
    except Exception:
        pass

    return packages

def get_updates():
    """
    Sucht nach verfügbaren Updates für Pacman, AUR und Flatpak.
    Gibt eine Liste von Paketen zurück, die aktualisiert werden können.
    """
    updates = []

    # 1. --- Native & AUR Updates (checkupdates für Sicherheit nutzen) ---
    # 'checkupdates' ist Teil der pacman-contrib und sicher, da es nicht die DB sperrt.
    try:
        output = subprocess.check_output(["checkupdates"], text=True, stderr=subprocess.DEVNULL)
        for line in output.splitlines():
            # Format: name alt-version -> neu-version
            parts = line.split()
            if len(parts) >= 4:
                updates.append({
                    "name": parts[0],
                    "source": "CachyOS Repo",
                    "version": f"{parts[1]} ➔ {parts[3]}",
                    "description": "System-Update verfügbar",
                    "update_available": True
                })
    except Exception:
        pass # Keine Updates oder Tool nicht installiert

    # 2. --- Flatpak Updates ---
    try:
        # flatpak update --dry-run zeigt an, was aktualisiert werden würde
        output = subprocess.check_output(
            ["flatpak", "remote-ls", "--updates", "--columns=application,version,origin"],
            text=True, stderr=subprocess.DEVNULL
        )
        for line in output.splitlines():
            parts = line.split('\t')
            if len(parts) >= 3:
                updates.append({
                    "name": parts[0],
                    "source": "Flathub" if "flathub" in parts[2].lower() else "Flatpak",
                    "version": f"➔ {parts[1]}",
                    "description": "App-Update verfügbar",
                    "update_available": True
                })
    except Exception:
        pass

    return updates