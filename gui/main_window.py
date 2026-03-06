from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QSizePolicy
)
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt, QParallelAnimationGroup
from .package_list import PackageListWidget
from .package_detail import PackageDetailWidget
from repos.veloxos import VeloxOSRepo
from repos.flathub import FlathubRepo
from repos.aur import AURRepo
from .settings import SettingsDialog
from core.system_packages import get_installed_packages, get_updates


class MainWindow(QMainWindow):
    """Hauptfenster mit Sidebar, Paketliste und animierter Detailansicht."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VeloxOS Package Manager")
        self.resize(1150, 720)

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

        self.top_sidebar = QListWidget()
        self.top_sidebar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.top_sidebar.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.top_sidebar.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Nur noch die funktionalen Hauptkategorien
        for t in ["Entdecken", "Installiert", "Updates"]:
            item = QListWidgetItem(t)
            self.top_sidebar.addItem(item)

        sidebar_layout.addWidget(self.top_sidebar)

        self.settings_btn = QPushButton("Einstellungen")
        sidebar_layout.addWidget(self.settings_btn)

        # --- Paketliste ---
        self.pkg_list_widget = PackageListWidget(self)

        # --- Detailbereich ---
        self.detail_widget = PackageDetailWidget(self)
        self.detail_widget.setFixedWidth(0)

        # --- Layout Links: Sidebar + Liste ---
        left_container = QWidget()
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        left_layout.addWidget(sidebar_container)
        left_layout.addWidget(self.pkg_list_widget)

        main_layout.addWidget(left_container, 1)
        main_layout.addWidget(self.detail_widget)

        # --- Animation Setup ---
        self.animation = QPropertyAnimation(self.detail_widget, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.max_animation = QPropertyAnimation(self.detail_widget, b"maximumWidth")
        self.max_animation.setDuration(300)
        self.max_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.anim_group = QParallelAnimationGroup()
        self.anim_group.addAnimation(self.animation)
        self.anim_group.addAnimation(self.max_animation)

        self.detail_target_width = 450
        self.detail_visible = False
        self.current_selected_pkg_id = None

        # --- Repos ---
        self.cachyos_repo = VeloxOSRepo()
        self.flathub_repo = FlathubRepo()
        self.aur_repo = AURRepo()

        # --- Signale ---
        self.top_sidebar.currentItemChanged.connect(self.on_category_changed)
        self.pkg_list_widget.list.itemClicked.connect(self.on_item_clicked)
        self.settings_btn.clicked.connect(self.on_settings_clicked)

        # Initial laden
        self.top_sidebar.setCurrentRow(0)

    def on_item_clicked(self, item, column):
        pkg = item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(pkg, dict): return

        pkg_id = f"{pkg.get('source')}_{pkg.get('name')}"

        if self.detail_visible and self.current_selected_pkg_id == pkg_id:
            self.hide_detail()
            self.pkg_list_widget.list.clearSelection()
        else:
            self.current_selected_pkg_id = pkg_id
            self.detail_widget.set_package(pkg)
            if not self.detail_visible:
                self.show_detail()

    def show_detail(self):
        self.anim_group.stop()
        self.animation.setStartValue(self.detail_widget.width())
        self.animation.setEndValue(self.detail_target_width)
        self.max_animation.setStartValue(self.detail_widget.width())
        self.max_animation.setEndValue(self.detail_target_width)
        self.anim_group.start()
        self.detail_visible = True

    def hide_detail(self):
        self.anim_group.stop()
        self.animation.setStartValue(self.detail_widget.width())
        self.animation.setEndValue(0)
        self.max_animation.setStartValue(self.detail_widget.width())
        self.max_animation.setEndValue(0)
        self.anim_group.start()
        self.detail_visible = False
        self.current_selected_pkg_id = None

    def on_category_changed(self, current, previous):
        if not current: return
        section = current.text()

        self.statusBar().showMessage(f"Lade {section}...")

        if section == "Entdecken":
            self.show_all_packages()
        elif section == "Installiert":
            installed = get_installed_packages()
            self.pkg_list_widget.set_packages(installed)
        elif section == "Updates":
            updatable = get_updates()
            self.pkg_list_widget.set_packages(updatable)
            if not updatable:
                self.statusBar().showMessage("Keine Updates verfügbar.", 5000)
        else:
            self.pkg_list_widget.set_packages([])

        if self.detail_visible:
            self.hide_detail()

    def on_settings_clicked(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def show_all_packages(self):
        packages = []
        packages += self.cachyos_repo.get_available_packages()
        packages += self.flathub_repo.get_available_packages()
        packages += self.aur_repo.get_available_packages()
        self.pkg_list_widget.set_packages(packages)
        self.statusBar().showMessage("Alle verfügbaren Pakete geladen.", 3000)