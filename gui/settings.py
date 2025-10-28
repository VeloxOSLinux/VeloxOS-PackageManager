from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt, QRect, QSize, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QPainter
from core import db, system_check

# -------------------------------------------------------------------
# QSwitch – animierter Toggle
# -------------------------------------------------------------------
class QSwitch(QWidget):
    def __init__(self, parent=None, checked=False):
        super().__init__(parent)
        self._checked = checked
        self._circle_position = 1 if checked else 0
        self._animation = QPropertyAnimation(self, b"circle_position", self)
        self._animation.setDuration(130)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(50, 28)
        self.clicked = lambda state: None

    def sizeHint(self):
        return QSize(50, 28)

    def get_circle_position(self):
        return self._circle_position

    def set_circle_position(self, pos):
        self._circle_position = pos
        self.update()

    circle_position = pyqtProperty(float, fget=get_circle_position, fset=set_circle_position)

    def mousePressEvent(self, event):
        self.toggle()
        super().mousePressEvent(event)

    def isChecked(self):
        return self._checked

    def setChecked(self, state: bool):
        if self._checked != state:
            self._checked = state
            self._animate()

    def toggle(self):
        self._checked = not self._checked
        self._animate()
        self.clicked(self._checked)

    def _animate(self):
        start = 1 if not self._checked else 0
        end = 0 if not self._checked else 1
        self._animation.stop()
        self._animation.setStartValue(start)
        self._animation.setEndValue(end)
        self._animation.start()
        self.update()

    def paintEvent(self, event):
        radius = self.height() / 2
        width = self.width()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        palette = self.palette()
        bg_on = palette.highlight().color()
        bg_off = palette.mid().color()
        circle_color = palette.base().color()

        painter.setBrush(bg_on if self._checked else bg_off)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, width, self.height(), radius, radius)

        circle_x = 2 + self._circle_position * (width - self.height())
        painter.setBrush(circle_color)
        painter.drawEllipse(QRect(int(circle_x), 2, int(self.height() - 4), int(self.height() - 4)))

# -------------------------------------------------------------------
# SettingsDialog
# -------------------------------------------------------------------
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Einstellungen")
        self.resize(420, 240)
        self.setModal(True)

        db.init_db()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        header = QLabel("Einstellungen")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 16pt; font-weight: bold;")
        main_layout.addWidget(header)

        info = QLabel("Repos aktivieren oder deaktivieren:")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(info)

        repos_container = QWidget()
        repos_layout = QVBoxLayout(repos_container)
        repos_layout.setSpacing(12)

        # Flathub
        self.flathub_switch = QSwitch(checked=False)
        self.add_repo_row(repos_layout, "Flathub", self.flathub_switch)

        # AUR
        self.aur_switch = QSwitch(checked=False)
        self.add_repo_row(repos_layout, "AUR", self.aur_switch)

        main_layout.addWidget(repos_container)

        # Schließen
        close_btn = QPushButton("Schließen")
        close_btn.clicked.connect(self.close)
        main_layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Systemstatus prüfen
        self.sync_system_status()

        # Events
        self.flathub_switch.clicked = self.on_flathub_toggled
        self.aur_switch.clicked = self.on_aur_toggled

    def add_repo_row(self, layout, name: str, switch: QSwitch):
        row = QHBoxLayout()
        label = QLabel(name)
        label.setStyleSheet("font-weight: 500; font-size: 11pt;")
        row.addWidget(label)
        row.addStretch()
        row.addWidget(switch)
        layout.addLayout(row)

    def sync_system_status(self):
        flathub_active = system_check.is_flathub_enabled()
        aur_active = system_check.is_aur_enabled()

        db.set_repo_status("flathub", flathub_active)
        db.set_repo_status("aur", aur_active)

        self.flathub_switch.setChecked(flathub_active)
        self.aur_switch.setChecked(aur_active)

    def on_flathub_toggled(self, enabled: bool):
        db.set_repo_status("flathub", enabled)
        if enabled:
            if system_check.enable_flathub():
                QMessageBox.information(self, "Flathub", "Flathub aktiviert.")
            else:
                QMessageBox.warning(self, "Fehler", "Flathub konnte nicht aktiviert werden.")
                self.flathub_switch.setChecked(False)
        else:
            if system_check.disable_flathub():
                QMessageBox.information(
                    self, "Flathub",
                    "Flathub wurde deaktiviert.\nDas Repo bleibt im System, wird aber vom Tool ignoriert."
                )
                db.set_repo_status("flathub", False)
            else:
                QMessageBox.warning(self, "Fehler", "Fehler beim Deaktivieren.")
                self.flathub_switch.setChecked(True)
                db.set_repo_status("flathub", True)

    def on_aur_toggled(self, enabled: bool):
        if enabled:
            success = system_check.enable_aur()
            db.set_repo_status("aur", success)
            self.aur_switch.setChecked(success)
            if success:
                QMessageBox.information(self, "AUR", "AUR ist jetzt aktiv.")
            else:
                QMessageBox.warning(self, "Fehler", "AUR konnte nicht aktiviert werden.")
        else:
            system_check.disable_aur()
            db.set_repo_status("aur", False)
            self.aur_switch.setChecked(False)
            QMessageBox.information(self, "AUR", "AUR wurde deaktiviert (yay bleibt installiert).")
