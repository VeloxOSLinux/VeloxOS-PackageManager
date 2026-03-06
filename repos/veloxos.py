import urllib.request
import tarfile
import tempfile
import os


class VeloxOSRepo:
    """VeloxOS Repo - liest Pakete, Versionen und Beschreibungen direkt aus den Repo-DBs."""

    def __init__(self):
        self.repo_name = "VeloxOS Repo"
        self.repos = {
            "core": "https://downloads.veloxos.org/repos/stable/core/veloxos-core.db",
            "v3": "https://downloads.veloxos.org/repos/stable/v3/veloxos-v3.db",
            "v4": "https://downloads.veloxos.org/repos/stable/v4/veloxos-v4.db",
        }

    def _read_db(self, url):
        packages = []

        try:
            # Temporäre Datei für den Download der .db
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                urllib.request.urlretrieve(url, tmp_file.name)
                tmp_path = tmp_file.name

            # Das .db-Format von pacman ist ein Tarball
            with tarfile.open(tmp_path, "r:*") as tar:
                for member in tar.getmembers():
                    # Jedes Paket hat einen Ordner mit einer 'desc' Datei
                    if member.name.endswith("/desc"):
                        f = tar.extractfile(member)
                        if f:
                            content = f.read().decode("utf-8", errors="ignore")

                            name = None
                            version = None
                            description = "Keine Beschreibung verfügbar."

                            lines = [line.strip() for line in content.splitlines()]

                            for i, line in enumerate(lines):
                                if line == "%NAME%":
                                    name = lines[i + 1]
                                elif line == "%VERSION%":
                                    version = lines[i + 1]
                                elif line == "%DESC%":
                                    description = lines[i + 1]

                            if name:
                                packages.append({
                                    "name": name,
                                    "source": self.repo_name,
                                    "version": version or "(unbekannt)",
                                    "description": description,
                                    # Da Pacman-Repos keine Icon-URLs liefern,
                                    # lassen wir das Feld leer, damit die GUI lokal sucht
                                    "icon_url": ""
                                })

            # Aufräumen
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        except Exception as e:
            print(f"[VeloxOS Repo] Fehler beim Lesen von {url}: {e}")

        return packages

    def get_available_packages(self):
        """Holt alle Pakete aus allen definierten VeloxOS Repositories."""
        all_packages = []
        for repo_shortname, url in self.repos.items():
            all_packages.extend(self._read_db(url))
        return all_packages