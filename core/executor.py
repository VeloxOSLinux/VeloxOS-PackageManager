import subprocess
import os


def get_install_command(name, source, is_update=False):
    """Gibt den Befehl zurück, der ausgeführt werden soll."""
    if "Flathub" in source or "Flatpak" in source:
        return ["flatpak", "install", "-y", "flathub", name]

    elif "AUR" in source:
        for helper in ["yay", "paru"]:
            if subprocess.call(["which", helper], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                # AUR Helper brauchen oft ein Pseudoterminal, wir nutzen hier die Standard-Variante
                return [helper, "-S", "--noconfirm", name]

    # Standard: Pacman via pkexec (öffnet den KDE-Passwortdialog)
    return ["pkexec", "pacman", "-S", "--noconfirm", name]


def get_remove_command(name, source):
    if "Flathub" in source or "Flatpak" in source:
        return ["flatpak", "uninstall", "-y", name]

    elif "AUR" in source:
        for helper in ["yay", "paru"]:
            if subprocess.call(["which", helper], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                return [helper, "-Rns", "--noconfirm", name]

    return ["pkexec", "pacman", "-Rns", "--noconfirm", name]