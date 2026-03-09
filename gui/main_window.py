import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QSizePolicy
)
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt, QParallelAnimationGroup, QThread, pyqtSignal
from .package_list import PackageListWidget
from .package_detail import PackageDetailWidget
from repos.veloxos import VeloxOSRepo
from repos.flathub import FlathubRepo
from repos.aur import AURRepo
from .settings import SettingsDialog
from core.system_packages import get_installed_packages, get_updates
from core.db import get_all_packages_from_db, populate_initial_packages


# --- Hintergrund-Worker für den Refresh ---
class UpdateWorker(QThread):
    finished = pyqtSignal(list)

    def run(self):
        """Lädt die Repos neu, ohne die GUI zu blockieren."""
        # Das schreibt die neuen Daten (auch dein 15-min-Paket) in die DB
        populate_initial_packages()
        # Gibt die frischen Daten zurück an die GUI
        self.finished.emit(get_all_packages_from_db())


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

        # --- Sidebar ---
        sidebar_container = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        sidebar_container.setFixedWidth(180)

        self.top_sidebar = QListWidget()
        self.top_sidebar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.top_sidebar.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.top_sidebar.setFocusPolicy(Qt.FocusPolicy.NoFocus)

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

        # Initial laden (DB-First)
        self.top_sidebar.setCurrentRow(0)

        # --- Hintergrund-Update starten ---
        self.update_worker = UpdateWorker()
        self.update_worker.finished.connect(self.on_background_update_done)
        self.update_worker.start()

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
        self.animation.setEndValue(self.detail_target_width)
        self.max_animation.setEndValue(self.detail_target_width)
        self.anim_group.start()
        self.detail_visible = True

    def hide_detail(self):
        self.anim_group.stop()
        self.animation.setEndValue(0)
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
            self.pkg_list_widget.set_packages(get_installed_packages())
        elif section == "Updates":
            updatable = get_updates()
            self.pkg_list_widget.set_packages(updatable)

        if self.detail_visible: self.hide_detail()

    def on_settings_clicked(self):
        SettingsDialog(self).exec()

    def show_all_packages(self):
        """Lädt sofort aus der lokalen DB."""
        packages = get_all_packages_from_db()
        self.pkg_list_widget.set_packages(packages)
        self.statusBar().showMessage(f"{len(packages)} Pakete geladen.", 2000)

    def on_background_update_done(self, new_pkgs):
        """Wird aufgerufen, wenn der Hintergrund-Scan fertig ist."""
        # Wenn der Nutzer gerade in "Entdecken" ist, Liste sanft aktualisieren
        if self.top_sidebar.currentItem() and self.top_sidebar.currentItem().text() == "Entdecken":
            self.pkg_list_widget.set_packages(new_pkgs)
            self.statusBar().showMessage("Paketliste wurde im Hintergrund aktualisiert.", 4000)