import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
# --- PFAD-FIX ENDE ---

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
# Jetzt finden wir die Module, da BASE_DIR im Pfad ist
from gui.main_window import MainWindow
from core.db import init_db, populate_initial_packages

def main():
    app = QApplication(sys.argv)

    # Icons und Styles nutzen jetzt das oben berechnete BASE_DIR
    icon_path = os.path.join(BASE_DIR, "icons", "logo.png")

    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Datenbank initialisieren
    init_db()
    populate_initial_packages()

    # Stylesheet laden
    style_path = os.path.join(BASE_DIR, "style", "style.qss")
    if os.path.exists(style_path):
        try:
            with open(style_path, "r") as f:
                app.setStyleSheet(f.read())
        except Exception as e:
            print(f"Fehler beim Laden des Stylesheets: {e}")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()