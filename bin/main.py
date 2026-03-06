import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon  # Wichtig für das Icon
from gui.main_window import MainWindow
from core.db import init_db, populate_initial_packages


def main():
    app = QApplication(sys.argv)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    icon_path = os.path.join(base_dir, "icons", "default.png")  # oder logo.png

    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))  # Setzt das Icon für die gesamte App

    init_db()
    populate_initial_packages()

    # Stylesheet laden
    style_path = os.path.join(base_dir, "style", "style.qss")
    if os.path.exists(style_path):
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()