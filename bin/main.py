import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from core.db import init_db, populate_initial_packages

def main():
    init_db()
    populate_initial_packages()  # Erststart: alle Pakete inkl. Beschreibung in DB

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
