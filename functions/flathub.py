import subprocess


class FlathubRepo:
    """
    Dummy-Implementierung eines Flathub-Repos.
    Später kannst du hier echte Flatpak-Abfragen einbauen.
    """

    def __init__(self):
        self.repo_name = "Flathub"

    def get_available_packages(self):
        """
        Liefert alle verfügbaren Flatpak-Pakete.
        Aktuell Dummy-Daten, später z. B. aus `flatpak remote-ls flathub` möglich.
        """
        try:
            # Beispiel für später (auskommentiert)
            # output = subprocess.check_output(["flatpak", "remote-ls", "flathub"], text=True)
            # packages = self._parse_flatpak_output(output)
            # return packages

            # Dummy-Daten
            packages = [
                {"name": "GIMP", "source": self.repo_name,
                 "description": "GNU Image Manipulation Program (Flatpak Dummy)"},
                {"name": "Firefox", "source": self.repo_name,
                 "description": "Mozilla Firefox Webbrowser (Flatpak Dummy)"},
                {"name": "VSCode", "source": self.repo_name,
                 "description": "Visual Studio Code Editor (Flatpak Dummy)"},
            ]
            return packages
        except Exception as e:
            print(f"[FlathubRepo] Fehler beim Abrufen der Pakete: {e}")
            return []

    def _parse_flatpak_output(self, output):
        """Hilfsfunktion für spätere echte Flatpak-Ausgabe."""
        packages = []
        for line in output.splitlines():
            name = line.strip()
            if name:
                packages.append({
                    "name": name,
                    "source": self.repo_name,
                    "description": "(keine Beschreibung verfügbar)"
                })
        return packages
