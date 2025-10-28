from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QBrush
import os


class PackageListWidget(QWidget):
    """Paketliste mit Filterbuttons, Suchfeld und Icons."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.icons_path = os.path.join(os.path.dirname(__file__), "..", "icons")
        self.all_packages = []
        self.current_filter = "Alle"
        self.search_query = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # --- Filterbuttons ---
        self.filter_bar = QHBoxLayout()
        self.filter_buttons = {}
        for label in ["Alle", "CachyOS Repo", "Flathub", "AUR"]:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.clicked.connect(self.on_filter_clicked)
            self.filter_bar.addWidget(btn)
            self.filter_buttons[label] = btn

        self.filter_buttons["Alle"].setChecked(True)
        layout.addLayout(self.filter_bar)

        # --- Suchfeld ---
        self.search = QLineEdit(self)
        self.search.setPlaceholderText("Pakete suchen …")
        self.search.textChanged.connect(self.on_search_changed)
        layout.addWidget(self.search)

        # --- Paketliste (QTreeWidget) ---
        self.list = QTreeWidget(self)
        self.list.setColumnCount(2)
        self.list.setHeaderLabels(["Paket", "Quelle"])
        self.list.setAlternatingRowColors(True)
        layout.addWidget(self.list)

        # --- Paketanzahl unten ---
        self.count_label = QLabel("0 Pakete", self)
        layout.addWidget(self.count_label)

        self.setLayout(layout)

    # ------------------------------

    def set_packages(self, packages):
        """Liste setzen und Filter/Recherche anwenden."""
        self.all_packages = packages
        self.refresh_list()

    def refresh_list(self):
        self.list.clear()
        query = self.search_query.lower()
        active_filter = self.current_filter
        count = 0

        for pkg in self.all_packages:
            name = pkg.get("name", "")
            source = pkg.get("source", "")

            if active_filter != "Alle" and source != active_filter:
                continue
            if query and query not in name.lower():
                continue

            icon_file = "cachy.png"
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
                icon_path = os.path.join(self.icons_path, "cachy.png")

            item = QTreeWidgetItem([name, source])
            item.setIcon(0, QIcon(icon_path))
            item.setData(0, Qt.ItemDataRole.UserRole, pkg)

            item.setTextAlignment(1, Qt.AlignmentFlag.AlignRight)
            self.list.addTopLevelItem(item)
            count += 1

        self.count_label.setText(f"{count} Pakete")

    # ------------------------------

    def on_filter_clicked(self):
        clicked_button = self.sender()
        if not clicked_button:
            return
        for btn in self.filter_buttons.values():
            btn.setChecked(btn is clicked_button)
        self.current_filter = clicked_button.text()
        self.refresh_list()

    def on_search_changed(self, text):
        self.search_query = text.strip()
        self.refresh_list()
