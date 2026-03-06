import os
import subprocess
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QPlainTextEdit, QProgressBar
)
from PyQt6.QtGui import QPixmap, QTextCursor
from PyQt6.QtCore import Qt, QProcess
from core.db import get_package_data
from repos.flathub import FlathubRepo
from core.executor import get_install_command, get_remove_command


class PackageDetailWidget(QWidget):
    """Detailansicht für Pakete mit integriertem Terminal und VeloxOS Design."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.icons_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "icons"))
        self.cache_path = os.path.join(self.icons_path, "cache")
        self.flathub_api = FlathubRepo()
        self.current_pkg = None
        self.process = QProcess(self)

        # Prozess-Signale verbinden
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.on_process_finished)

        # Layout-Setup
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # --- Header (Icon & Titel) ---
        header = QHBoxLayout()
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(80, 80)
        self.icon_label.setScaledContents(True)
        header.addWidget(self.icon_label)

        vbox = QVBoxLayout()
        self.title = QLabel("Paket auswählen")
        self.title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #00f2ff;")
        self.version_label = QLabel("-")
        self.version_label.setStyleSheet("color: #94a3b8; font-size: 11pt;")
        vbox.addWidget(self.title)
        vbox.addWidget(self.version_label)
        header.addLayout(vbox)
        layout.addLayout(header)

        self.source_label = QLabel("Quelle: -")
        self.source_label.setStyleSheet("color: #64748b; font-style: italic;")
        layout.addWidget(self.source_label)

        # --- Beschreibung (Scrollbar) ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        self.desc_label = QLabel("Wähle ein Paket aus der Liste aus, um Details zu sehen.")
        self.desc_label.setWordWrap(True)
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.desc_label.setStyleSheet("font-size: 11pt; line-height: 150%; color: #e0e6ed;")
        scroll.setWidget(self.desc_label)
        layout.addWidget(scroll, 1)

        # --- Terminal-Bereich (Fortschritt & Log) ---
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.terminal_output = QPlainTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.hide()
        # Monospace Font für Terminal-Optik
        self.terminal_output.setStyleSheet("""
            QPlainTextEdit { 
                background-color: #05070a; 
                color: #00f2ff; 
                border: 1px solid #1e293b;
                font-family: 'Fira Code', 'Monospace', 'Courier New';
                font-size: 9pt;
            }
        """)
        layout.addWidget(self.terminal_output)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        self.install_btn = QPushButton("Installieren")
        self.install_btn.setObjectName("install")
        self.remove_btn = QPushButton("Entfernen")
        self.remove_btn.setObjectName("remove")

        btn_layout.addWidget(self.install_btn)
        btn_layout.addWidget(self.remove_btn)
        layout.addLayout(btn_layout)

        # Signale
        self.install_btn.clicked.connect(self.on_install_clicked)
        self.remove_btn.clicked.connect(self.on_remove_clicked)

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode(errors='replace')
        self.terminal_output.appendPlainText(data)
        self.terminal_output.moveCursor(QTextCursor.MoveOperation.End)

        # Fortschritt parsen (z.B. pacman oder flatpak % Ausgaben)
        match = re.search(r'(\d+)%', data)
        if match:
            self.progress_bar.setValue(int(match.group(1)))

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode(errors='replace')
        self.terminal_output.appendPlainText(f"[INFO] {data}")

    def on_process_finished(self):
        self.install_btn.setEnabled(True)
        self.remove_btn.setEnabled(True)
        self.progress_bar.hide()
        if self.current_pkg:
            self.set_package(self.current_pkg)
        self.terminal_output.appendPlainText("\n>>> Vorgang abgeschlossen.")

    def run_command(self, cmd):
        self.terminal_output.show()
        self.terminal_output.clear()
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.install_btn.setEnabled(False)
        self.remove_btn.setEnabled(False)
        self.process.start(cmd[0], cmd[1:])

    def on_install_clicked(self):
        if self.current_pkg:
            cmd = get_install_command(self.current_pkg['name'], self.current_pkg['source'])
            self.run_command(cmd)

    def on_remove_clicked(self):
        if self.current_pkg:
            cmd = get_remove_command(self.current_pkg['name'], self.current_pkg['source'])
            self.run_command(cmd)

    def is_installed(self, name, source):
        try:
            if "Flat" in source:
                return subprocess.run(["flatpak", "info", name], capture_output=True).returncode == 0
            return subprocess.run(["pacman", "-Qq", name.lower()], capture_output=True).returncode == 0
        except:
            return False

    def set_package(self, pkg):
        if not pkg: return
        self.current_pkg = pkg

        name = pkg.get("name", "")
        source = pkg.get("source", "")
        db_data = get_package_data(source, name)

        # UI Texte setzen
        display_name = name.split(".")[-1] if "." in name else name
        self.title.setText(display_name)
        self.version_label.setText(f"Version: {pkg.get('version', db_data.get('version', 'N/A'))}")
        self.source_label.setText(f"Quelle: {source}")
        self.desc_label.setText(pkg.get("description", db_data.get("description", "Keine Beschreibung verfügbar.")))

        # Status prüfen
        installed = self.is_installed(name, source)
        self.install_btn.setEnabled(not installed)
        self.remove_btn.setEnabled(installed)

        # Icon laden
        pixmap = self.load_icon(name, pkg.get("icon_url", ""))
        self.icon_label.setPixmap(pixmap)

    def load_icon(self, name, icon_url):
        # Fallback auf lokales Cache/Icon
        clean = "".join([c for c in name if c.isalnum()]).lower()
        cache_path = os.path.join(self.cache_path, f"{clean}.png")
        if os.path.exists(cache_path): return QPixmap(cache_path)

        fallback = os.path.join(self.icons_path, "default.png")
        return QPixmap(fallback) if os.path.exists(fallback) else QPixmap()