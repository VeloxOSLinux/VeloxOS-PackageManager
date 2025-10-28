from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt
from core import db  # DB aus core-Ordner

class SettingsDialog(QDialog):
    """Dialog für Programmeinstellungen mit Repo-Status aus DB."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Einstellungen")
        self.resize(400, 200)
        self.setModal(True)

        db.init_db()  # DB initialisieren

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)

        header = QLabel("Einstellungen")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 16pt; font-weight: bold;")
        main_layout.addWidget(header)

        info = QLabel("Aktiviere die gewünschten Repos:")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(info)

        # --- Flathub ---
        flathub_container = QWidget()
        flathub_layout = QHBoxLayout(flathub_container)
        flathub_layout.setSpacing(10)

        self.flathub_btn = QPushButton("Flathub aktivieren")
        self.flathub_btn.setCheckable(True)
        self.flathub_status = QLabel("inaktiv")
        self.flathub_status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        flathub_layout.addWidget(self.flathub_btn)
        flathub_layout.addWidget(self.flathub_status)
        main_layout.addWidget(flathub_container)

        # --- AUR ---
        aur_container = QWidget()
        aur_layout = QHBoxLayout(aur_container)
        aur_layout.setSpacing(10)

        self.aur_btn = QPushButton("AUR aktivieren")
        self.aur_btn.setCheckable(True)
        self.aur_status = QLabel("inaktiv")
        self.aur_status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        aur_layout.addWidget(self.aur_btn)
        aur_layout.addWidget(self.aur_status)
        main_layout.addWidget(aur_container)

        # --- Schließen-Button ---
        close_btn = QPushButton("Schließen")
        close_btn.clicked.connect(self.close)
        main_layout.addWidget(close_btn)

        # --- Signale ---
        self.flathub_btn.toggled.connect(self.update_flathub_status)
        self.aur_btn.toggled.connect(self.update_aur_status)

        # --- Status aus DB laden ---
        self.flathub_btn.setChecked(db.get_repo_status("flathub"))
        self.aur_btn.setChecked(db.get_repo_status("aur"))

    # ----------------------------
    def update_flathub_status(self, checked: bool):
        db.set_repo_status("flathub", checked)
        if checked:
            self.flathub_status.setText("aktiv")
            self.flathub_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.flathub_status.setText("inaktiv")
            self.flathub_status.setStyleSheet("color: orange; font-weight: bold;")

    def update_aur_status(self, checked: bool):
        db.set_repo_status("aur", checked)
        if checked:
            self.aur_status.setText("aktiv")
            self.aur_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.aur_status.setText("inaktiv")
            self.aur_status.setStyleSheet("color: orange; font-weight: bold;")
