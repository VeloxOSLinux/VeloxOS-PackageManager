import sys
import os
import ctypes

# --- 1. PFAD-FIX ---
# Ermittle das Verzeichnis, in dem 'bin' liegt (z.B. /usr/share/velox-package-manager)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# --- 2. ICON-FIX (TASKBAR/DOCK) ---
# Wir setzen eine eindeutige ID, damit der Window-Manager das Fenster dem Icon zuordnet
APP_ID = 'velox-package-manager'
try:
    if os.name == 'nt':  # Windows-Kompatibilität
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
    else:
        # Unter Linux hilft es, die WM_CLASS direkt für Qt zu setzen
        os.environ["QT_QPA_PLATFORM"] = "wayland;xcb"
except Exception:
    pass

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from gui.main_window import MainWindow
from core.db import init_db


def main():
    # Setzt den Namen für das gesamte Anwendungs-Objekt
    app = QApplication(sys.argv)
    app.setApplicationName("VeloxOS Package Manager")
    app.setDesktopFileName(APP_ID)  # Wichtig für Wayland/GNOME/KDE

    # Icon-Pfad berechnen (Nutzt das Logo aus deinem icons/ Ordner)
    icon_path = os.path.join(BASE_DIR, "icons", "default.png")

    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
    else:
        print(f"[Warnung] Icon nicht gefunden unter: {icon_path}")

    # Datenbank initialisieren (Erstellt Ordner im User-Home)
    init_db()

    # Stylesheet laden
    style_path = os.path.join(BASE_DIR, "style", "style.qss")
    if os.path.exists(style_path):
        try:
            with open(style_path, "r") as f:
                app.setStyleSheet(f.read())
        except Exception as e:
            print(f"Fehler beim Laden des Stylesheets: {e}")

    # Hauptfenster initialisieren
    window = MainWindow()

    # Setzt die WM_CLASS für das Fenster (Match mit .desktop Datei)
    window.setObjectName(APP_ID)
    window.setWindowTitle("VeloxOS Package Manager")

    # Falls MainWindow eine eigene setWindowIcon Methode braucht:
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()