import urllib.request
import tarfile
import tempfile
import os
import xml.etree.ElementTree as ET
import gzip
from PyQt6.QtGui import QIcon


class VeloxOSRepo:
    def __init__(self):
        self.repo_name = "VeloxOS Repo"
        self.repos = {
            "core": "https://downloads.veloxos.org/repos/stable/core/veloxos-core.db",
            "v3": "https://downloads.veloxos.org/repos/stable/v3/veloxos-v3.db",
            "v4": "https://downloads.veloxos.org/repos/stable/v4/veloxos-v4.db",
        }
        self.appstream_map = {}
        self.icon_cache = {}
        self._load_appstream_data()

    def _load_appstream_data(self):
        """Lädt AppStream Daten für besseres Icon-Mapping."""
        xml_path = "/usr/share/app-info/xmls/archlinux.xml.gz"
        if not os.path.exists(xml_path): return
        try:
            with gzip.open(xml_path, 'rb') as f:
                root = ET.parse(f).getroot()
                for component in root.findall('component'):
                    pkg = component.findtext('pkgname')
                    icon = component.findtext('icon')
                    if pkg and icon:
                        self.appstream_map[pkg] = icon
        except:
            pass

    def _find_local_icon(self, pkg_name):
        """Sucht Icons gezielt an bekannten Orten statt die ganze Platte zu scannen."""
        if pkg_name in self.icon_cache:
            return self.icon_cache[pkg_name]

        icon_name = self.appstream_map.get(pkg_name, pkg_name)

        # 1. System-Theme Check (Blitzschnell)
        if QIcon.hasThemeIcon(icon_name):
            res = f"theme://{icon_name}"
            self.icon_cache[pkg_name] = res
            return res

        # 2. Gezielte Pfad-Suche
        paths = [
            f"/usr/share/icons/hicolor/scalable/apps/{icon_name}.svg",
            f"/usr/share/icons/hicolor/64x64/apps/{icon_name}.png",
            f"/usr/share/pixmaps/{icon_name}.png"
        ]
        for p in paths:
            if os.path.exists(p):
                self.icon_cache[pkg_name] = p
                return p

        return ""

    def _read_db(self, url):
        """Lädt und parst eine Repo-Datenbank."""
        packages = []
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                urllib.request.urlretrieve(url, tmp_file.name)
                tmp_path = tmp_file.name

            with tarfile.open(tmp_path, "r:*") as tar:
                for member in tar.getmembers():
                    if member.name.endswith("/desc"):
                        f = tar.extractfile(member)
                        if f:
                            content = f.read().decode("utf-8", errors="ignore")
                            name, ver, desc = "", "", ""
                            lines = content.splitlines()
                            for i, line in enumerate(lines):
                                if line == "%NAME%":
                                    name = lines[i + 1]
                                elif line == "%VERSION%":
                                    ver = lines[i + 1]
                                elif line == "%DESC%":
                                    desc = lines[i + 1]

                            if name:
                                packages.append({
                                    "name": name,
                                    "source": self.repo_name,
                                    "version": ver,
                                    "description": desc,
                                    "icon_url": self._find_local_icon(name)
                                })
            os.remove(tmp_path)
        except Exception as e:
            print(f"[VeloxOS] Fehler beim Lesen von {url}: {e}")
        return packages

    def get_available_packages(self):
        """Sammelt alle Pakete aus allen konfigurierten Repos."""
        all_packages = []
        for url in self.repos.values():
            all_packages.extend(self._read_db(url))
        return all_packages