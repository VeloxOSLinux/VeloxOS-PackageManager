from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class PackageDetailWidget(QWidget):
    """Rechte Detailansicht für ein ausgewähltes Paket."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            background-color: palette(base);
            border-left: 1px solid palette(dark);
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.title = QLabel("Paketname", self)
        self.title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(self.title)

        self.source_label = QLabel("Quelle: –", self)
        self.source_label.setStyleSheet("color: gray;")
        layout.addWidget(self.source_label)

        self.description = QLabel("Beschreibung des Pakets …", self)
        self.description.setWordWrap(True)
        layout.addWidget(self.description)

        self.install_btn = QPushButton("Installieren", self)
        self.install_btn.setFixedWidth(150)
        layout.addWidget(self.install_btn)

        layout.addStretch()

    def set_package(self, pkg):
        self.title.setText(pkg["name"])
        self.source_label.setText(f"Quelle: {pkg['source']}")
        self.description.setText(pkg["description"])
