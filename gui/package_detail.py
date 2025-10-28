from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QDialog
)
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtCore import Qt
import os
from core.db import get_package_description


class ImageDialog(QDialog):
    """Dialog zum Vergrößern eines Bildes."""
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bild vergrößert")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.resize(800, 600)
        self.setMinimumSize(400, 300)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

        self.original_pixmap = pixmap
        self.update_image()

    def resizeEvent(self, event):
        self.update_image()
        super().resizeEvent(event)

    def update_image(self):
        if self.original_pixmap and not self.original_pixmap.isNull():
            scaled = self.original_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.label.setPixmap(scaled)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        self.close()


class PackageDetailWidget(QWidget):
    """Detailansicht für ein ausgewähltes Paket."""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.icons_path = os.path.join(os.path.dirname(__file__), "..", "icons")
        self.current_pixmap = None

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # --- Paketname + Quelle ---
        self.title = QLabel("Paketname", self)
        self.title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(self.title)

        self.source_label = QLabel("Quelle: –", self)
        self.source_label.setStyleSheet("color: gray;")
        layout.addWidget(self.source_label)

        # --- Bild (Icon als Platzhalter) ---
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.image_label.setMaximumHeight(200)
        layout.addWidget(self.image_label)
        self.image_label.mousePressEvent = self.show_full_image

        # --- Scrollbare Beschreibung ---
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.desc_label = QLabel("Beschreibung des Pakets …", self)
        self.desc_label.setWordWrap(True)
        self.scroll_area.setWidget(self.desc_label)
        layout.addWidget(self.scroll_area, 1)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        self.install_btn = QPushButton("Installieren", self)
        self.update_btn = QPushButton("Update", self)
        self.remove_btn = QPushButton("Entfernen", self)
        btn_layout.addWidget(self.install_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.remove_btn)
        layout.addLayout(btn_layout)

        layout.addStretch()

    # -------------------------------------------------------

    def set_package(self, pkg):
        """Setzt alle Infos und Bild des Pakets."""
        name = pkg.get("name", "Unbekannt")
        source = pkg.get("source", "-")

        self.title.setText(name)
        self.source_label.setText(f"Quelle: {source}")

        # Beschreibung aus DB nachladen (Lazy Loading)
        desc = get_package_description(name, source)
        self.desc_label.setText(desc or "Keine Beschreibung verfügbar.")

        # Icon bestimmen
        icon_file = "default.png"
        lname = name.lower()
        if "cachy" in lname:
            icon_file = "cachy.png"
        elif "firefox" in lname:
            icon_file = "firefox.png"
        elif "gimp" in lname:
            icon_file = "gimpicon.png"
        elif "libre" in lname:
            icon_file = "libreoffice.png"
        elif "spotify" in lname:
            icon_file = "spotify.png"
        elif "vscode" in lname:
            icon_file = "vscode.png"

        icon_path = os.path.join(self.icons_path, icon_file)
        if not os.path.exists(icon_path):
            icon_path = os.path.join(self.icons_path, "default.png")

        self.current_pixmap = QPixmap(icon_path)
        scaled_pixmap = self.current_pixmap.scaledToHeight(
            200, Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

    # -------------------------------------------------------
    def show_full_image(self, event):
        """Öffnet Popup mit vergrößertem Bild."""
        if self.current_pixmap and not self.current_pixmap.isNull():
            dialog = ImageDialog(self.current_pixmap, self)
            dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
            dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            dialog.show()
