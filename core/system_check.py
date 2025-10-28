import shutil
import subprocess
from PyQt6.QtWidgets import QMessageBox

# -------------------------------------------------------------------
# Flathub
# -------------------------------------------------------------------
def is_flathub_enabled() -> bool:
    try:
        result = subprocess.run(
            ["flatpak", "remotes"],
            capture_output=True,
            text=True,
            check=True
        )
        return "flathub" in result.stdout.lower()
    except subprocess.CalledProcessError:
        return False

def enable_flathub() -> bool:
    try:
        subprocess.run(
            ["flatpak", "remote-add", "--if-not-exists",
             "flathub", "https://flathub.org/repo/flathub.flatpakrepo"],
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def disable_flathub() -> bool:
    """
    Flathub wird nur für das Tool deaktiviert.
    Keine Änderungen am System.
    """
    return True

# -------------------------------------------------------------------
# AUR – nur yay
# -------------------------------------------------------------------
def is_aur_enabled() -> bool:
    """Prüft, ob yay auf dem System existiert."""
    return shutil.which("yay") is not None

def enable_aur() -> bool:
    """Versuche, yay zu installieren, falls nicht vorhanden."""
    if is_aur_enabled():
        return True  # yay vorhanden → alles gut

    if not shutil.which("pkexec"):
        QMessageBox.warning(None, "Fehler", "pkexec nicht verfügbar. Bitte yay manuell installieren.")
        return False

    reply = QMessageBox.question(
        None,
        "AUR aktivieren",
        "Kein AUR-Helper gefunden. 'yay' installieren?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    if reply != QMessageBox.StandardButton.Yes:
        return False

    try:
        subprocess.run(["pkexec", "pacman", "-S", "--noconfirm", "yay"], check=True)
        return is_aur_enabled()
    except subprocess.CalledProcessError:
        QMessageBox.warning(None, "Fehler", "Installation von yay fehlgeschlagen.")
        return False

def disable_aur() -> bool:
    """Logische Deaktivierung; yay bleibt installiert."""
    return True
