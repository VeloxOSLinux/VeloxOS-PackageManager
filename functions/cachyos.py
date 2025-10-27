import subprocess


class CachyOSRepo:
    """
    Dummy-Implementierung eines CachyOS-Repos.
    Später kannst du hier echte pacman/reflector-Abfragen einbauen.
    """

    def __init__(self):
        self.repo_name = "CachyOS Repo"

    def get_available_packages(self):
        """
        Liefert alle verfügbaren Pakete aus dem CachyOS-Repo.
        Aktuell Dummy-Daten, kann später z. B. aus `pacman -Sl cachyos` kommen.
        """
        try:
            # Beispiel für später (auskommentiert, da Dummy)
            # output = subprocess.check_output(["pacman", "-Sl", "cachyos"], text=True)
            # packages = self._parse_pacman_output(output)
            # return packages

            # Dummy-Daten
            packages = [
                {"name": "linux-cachyos", "source": self.repo_name,
                 "description": "Optimierter Linux-Kernel von CachyOS"},
                {"name": "cachyos-settings", "source": self.repo_name,
                 "description": "Systemweite Standardkonfiguration für CachyOS"},
                {"name": "cachyos-gtk-theme", "source": self.repo_name,
                 "description": "Das offizielle GTK-Theme von CachyOS"},
                {"name": "cachyos-wallpapers", "source": self.repo_name,
                 "description": "Hintergrundbilder für CachyOS"},
            ]
            return packages
        except Exception as e:
            print(f"[CachyOSRepo] Fehler beim Abrufen der Pakete: {e}")
            return []

    def _parse_pacman_output(self, output):
        """Hilfsfunktion für spätere echte pacman-Ausgabe."""
        packages = []
        for line in output.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                packages.append({
                    "name": parts[1],
                    "source": self.repo_name,
                    "description": "(keine Beschreibung verfügbar)"
                })
        return packages
