from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QSizePolicy
)
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt
from .package_list import PackageListWidget
from .package_detail import PackageDetailWidget
from repos.cachyos import CachyOSRepo
from repos.flathub import FlathubRepo
from repos.aur import AURRepo
from .settings import SettingsDialog
from core.system_packages import get_installed_packages


class MainWindow(QMainWindow):
    """Hauptfenster mit Sidebar und Paketliste."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CachyOS Package Manager")
        self.resize(1000, 650)

        # --- Zentralwidget + Hauptlayout ---
        central = QWidget(self)
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- Sidebar Container ---
        sidebar_container = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        sidebar_container.setFixedWidth(180)

        # --- Obere Sidebar: Navigation + Kategorien ---
        self.top_sidebar = QListWidget()
        self.top_sidebar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.top_sidebar.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.top_sidebar.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        for t in ["Entdecken", "Installiert", "Updates"]:
            item = QListWidgetItem(t)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.top_sidebar.addItem(item)

        # Trenner
        item = QListWidgetItem("────────────")
        item.setFlags(Qt.ItemFlag.NoItemFlags)
        self.top_sidebar.addItem(item)

        # Dummy-Kategorien
        for c in ["Musterkategorie1", "Musterkategorie2"]:
            item = QListWidgetItem(c)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.top_sidebar.addItem(item)

        sidebar_layout.addWidget(self.top_sidebar)

        # --- Untere Sidebar: Einstellungen ---
        self.settings_btn = QPushButton("Einstellungen")
        self.settings_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sidebar_layout.addWidget(self.settings_btn)

        # --- Paketliste ---
        self.pkg_list_widget = PackageListWidget(self)
        self.pkg_list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # --- Detailbereich ---
        self.detail_widget = PackageDetailWidget(self)
        self.detail_widget.setFixedWidth(0)

        # --- Layout links: Sidebar + Paketliste ---
        left_container = QWidget()
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        left_layout.addWidget(sidebar_container)
        left_layout.addWidget(self.pkg_list_widget)

        main_layout.addWidget(left_container)
        main_layout.addWidget(self.detail_widget)

        # --- Animation Detailbereich ---
        self.animation = QPropertyAnimation(self.detail_widget, b"maximumWidth")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.detail_target_width = 400
        self.detail_visible = False

        # --- Repos ---
        self.cachyos_repo = CachyOSRepo()
        self.flathub_repo = FlathubRepo()
        self.aur_repo = AURRepo()

        # --- Signale ---
        self.top_sidebar.currentItemChanged.connect(self.on_category_changed)
        self.pkg_list_widget.list.itemClicked.connect(self.on_item_clicked)
        self.settings_btn.clicked.connect(self.on_settings_clicked)

        # --- Initial laden ---
        self.top_sidebar.setCurrentRow(0)

    # ----------------------------

    def on_item_clicked(self, item, column):
        pkg = item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(pkg, dict):
            return
        self.detail_widget.set_package(pkg)
        if not self.detail_visible:
            self.show_detail()

    def show_detail(self):
        self.animation.stop()
        self.animation.setStartValue(self.detail_widget.width())
        self.animation.setEndValue(self.detail_target_width)
        self.animation.start()
        self.detail_visible = True

    def hide_detail(self):
        self.animation.stop()
        self.animation.setStartValue(self.detail_widget.width())
        self.animation.setEndValue(0)
        self.animation.start()
        self.detail_visible = False

    # ----------------------------

    def on_category_changed(self, current, previous):
        if not current:
            return

        section = current.text()
        if section == "Entdecken":
            self.show_all_packages()
        elif section == "Installiert":
            installed = get_installed_packages()
            self.pkg_list_widget.set_packages(installed)
        elif section == "Updates":
            # Update-Logik später
            self.pkg_list_widget.set_packages([])
        else:
            # Dummy-Kategorien
            self.pkg_list_widget.set_packages([])

        self.hide_detail()

    def on_settings_clicked(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    # ----------------------------

    def show_all_packages(self):
        packages = []
        packages += self.cachyos_repo.get_available_packages()
        packages += self.flathub_repo.get_available_packages()
        packages += self.aur_repo.get_available_packages()
        self.pkg_list_widget.set_packages(packages)
