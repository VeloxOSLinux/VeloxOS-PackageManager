from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt


class PackageListWidget(QWidget):
    """Paketliste mit Suchfeld und Filterbuttons."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Filterbuttons
        self.filter_bar = QHBoxLayout()
        self.filter_buttons = {}
        for label in ["Alle", "CachyOS Repo", "Pacman", "Flathub", "AUR"]:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setStyleSheet("")
            btn.clicked.connect(self.on_filter_clicked)
            self.filter_bar.addWidget(btn)
            self.filter_buttons[label] = btn

        self.filter_buttons["Alle"].setChecked(True)
        layout.addLayout(self.filter_bar)

        # Suchfeld
        self.search = QLineEdit(self)
        self.search.setPlaceholderText("Pakete suchen …")
        self.search.textChanged.connect(self.on_search_changed)
        layout.addWidget(self.search)

        # Paketliste
        self.list = QListWidget(self)
        self.list.setAlternatingRowColors(True)
        layout.addWidget(self.list)

        self.current_filter = "Alle"
        self.search_query = ""

    def populate_packages(self, packages):
        self.list.clear()
        for pkg in packages:
            display_text = f"{pkg['name']:<40} [{pkg['source']}]"
            item = QListWidgetItem(display_text)
            item.setData(0, pkg)
            self.list.addItem(item)

    def on_filter_clicked(self):
        clicked_button = self.sender()
        label = clicked_button.text()
        for btn in self.filter_buttons.values():
            btn.setChecked(btn is clicked_button)
        self.current_filter = label

    def on_search_changed(self, text):
        self.search_query = text
