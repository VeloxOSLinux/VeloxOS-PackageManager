import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QTreeWidget, QTreeWidgetItem, QLabel, QHeaderView)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon


class PackageListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.icons_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "icons"))
        self.cache_path = os.path.join(self.icons_path, "cache")

        self.all_packages = []
        self.current_filter = "Alle"
        self.search_query = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # --- Filter ---
        self.filter_bar = QHBoxLayout()
        self.filter_buttons = {}
        for label in ["Alle", "VeloxOS Repo", "Flathub", "AUR"]:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.clicked.connect(self.on_filter_clicked)
            self.filter_bar.addWidget(btn)
            self.filter_buttons[label] = btn
        self.filter_buttons["Alle"].setChecked(True)
        layout.addLayout(self.filter_bar)

        # --- Suche ---
        self.search = QLineEdit(self)
        self.search.setPlaceholderText("Pakete suchen …")
        self.search.textChanged.connect(self.on_search_changed)
        layout.addWidget(self.search)

        # --- Liste ---
        self.list = QTreeWidget(self)
        self.list.setColumnCount(2)
        self.list.setHeaderLabels(["Paket", "Quelle"])
        self.list.setAlternatingRowColors(True)
        self.list.setIconSize(QSize(32, 32))
        self.list.setUniformRowHeights(True)

        # --- SPALTEN-FIX ---
        # Das sorgt dafür, dass die erste Spalte den Platz einnimmt
        header = self.list.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.list)

        self.count_label = QLabel("0 Pakete", self)
        layout.addWidget(self.count_label)

    def set_packages(self, packages):
        self.all_packages = packages
        self.refresh_list()

    def format_display_name(self, pkg_name):
        """Macht aus org.gimp.GIMP -> GIMP"""
        if "." in pkg_name:
            parts = pkg_name.split(".")
            # Wir nehmen das letzte Element, außer es ist was generisches wie 'desktop'
            display_name = parts[-1]
            if display_name.lower() in ["desktop", "app"] and len(parts) > 1:
                display_name = parts[-2]
            return display_name
        return pkg_name

    def get_icon(self, pkg):
        icon_data = pkg.get("icon_url", "")

        if not icon_data:
            return QIcon(os.path.join(self.icons_path, "default.png"))

        # Falls es ein lokaler Pfad ist (beginnt mit /)
        if icon_data.startswith("/"):
            if os.path.exists(icon_data):
                return QIcon(icon_data)

        # Falls es eine URL ist (Flathub Logik aus vorigem Schritt)
        clean_name = "".join([c for c in pkg.get("name", "") if c.isalnum()]).lower()
        cache_file = os.path.join(self.cache_path, f"{clean_name}.png")
        if os.path.exists(cache_file):
            return QIcon(cache_file)

        return QIcon(os.path.join(self.icons_path, "default.png"))

    def refresh_list(self):
        self.list.clear()
        query = self.search_query.lower()
        active_filter = self.current_filter

        self.list.setUpdatesEnabled(False)

        items = []
        for pkg in self.all_packages:
            raw_name = pkg.get("name", "")
            source = pkg.get("source", "")

            # Filtern nach technischem Namen oder Anzeigenamen
            display_name = self.format_display_name(raw_name)

            if active_filter != "Alle" and source != active_filter:
                continue
            if query and (query not in raw_name.lower() and query not in display_name.lower()):
                continue

            item = QTreeWidgetItem([display_name, source])
            item.setIcon(0, self.get_icon(pkg))
            item.setData(0, Qt.ItemDataRole.UserRole, pkg)
            items.append(item)

        self.list.addTopLevelItems(items)
        self.list.setUpdatesEnabled(True)
        self.count_label.setText(f"{len(items)} Pakete")

    def on_filter_clicked(self):
        btn = self.sender()
        for b in self.filter_buttons.values(): b.setChecked(b is btn)
        self.current_filter = btn.text()
        self.refresh_list()

    def on_search_changed(self, text):
        self.search_query = text.strip()
        self.refresh_list()