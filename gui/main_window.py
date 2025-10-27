from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QListWidget
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
from .package_list import PackageListWidget
from .package_detail import PackageDetailWidget
from functions.cachyos import CachyOSRepo


class MainWindow(QMainWindow):
    """Hauptfenster mit animierter Detailansicht (Breitenanimation)."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CachyOS Package Manager")
        self.resize(1000, 650)

        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        # Seitenleiste
        self.sidebar = QListWidget(self)
        self.sidebar.addItems(["Entdecken", "CachyOS Repo", "Installiert", "Updates", "Einstellungen"])
        self.sidebar.setFixedWidth(180)
        layout.addWidget(self.sidebar)

        # Container für Liste + Detail
        self.container = QWidget(self)
        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        layout.addWidget(self.container)

        # Paketliste
        self.pkg_list_widget = PackageListWidget(self)
        container_layout.addWidget(self.pkg_list_widget)

        # Detailansicht (startet unsichtbar)
        self.detail_widget = PackageDetailWidget(self)
        self.detail_widget.setFixedWidth(0)
        container_layout.addWidget(self.detail_widget)

        # Animation
        self.animation = QPropertyAnimation(self.detail_widget, b"maximumWidth")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Repos initialisieren
        self.cachyos_repo = CachyOSRepo()

        # Sidebar-Aktionen
        self.sidebar.currentItemChanged.connect(self.on_category_changed)
        self.pkg_list_widget.list.itemClicked.connect(self.on_item_clicked)

        # Zustand
        self.detail_visible = False
        self.detail_target_width = 400

        # Standardansicht: Entdecken (zeigt CachyOS-Pakete)
        self.show_cachyos_packages()

    def on_item_clicked(self, item):
        pkg = item.data(0)
        if not pkg:
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

    def on_category_changed(self, current, previous):
        if not current:
            return

        section = current.text()
        if section == "CachyOS Repo":
            self.show_cachyos_packages()
        elif section == "Entdecken":
            self.show_cachyos_packages()
        else:
            self.pkg_list_widget.populate_packages([])
        self.hide_detail()

    def show_cachyos_packages(self):
        packages = self.cachyos_repo.get_available_packages()
        self.pkg_list_widget.populate_packages(packages)
