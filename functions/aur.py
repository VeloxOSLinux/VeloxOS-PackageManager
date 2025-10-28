import subprocess


class AURRepo:
    """
    Dummy-Implementierung eines AUR-Repos.
    Später können hier echte AUR-Abfragen z.B. via yay oder aurweb API eingebaut werden.
    """

    def __init__(self):
        self.repo_name = "AUR"

    def get_available_packages(self):
        """
        Liefert Dummy-Pakete aus AUR zurück.
        """
        try:
            # Beispiel für später (auskommentiert)
            # output = subprocess.check_output(["yay", "-Sl"], text=True)
            # packages = self._parse_aur_output(output)
            # return packages

            packages = [
                {"name": "gimp", "source": self.repo_name,
                 "description": "GNU Image Manipulation Program (AUR Dummy)"},
                {"name": "firefox", "source": self.repo_name,
                 "description": "Mozilla Firefox Webbrowser (AUR Dummy)"},
                {"name": "vscode", "source": self.repo_name,
                 "description": "Visual Studio Code Editor (AUR Dummy)"},
            ]
            return packages
        except Exception as e:
            print(f"[AURRepo] Fehler beim Abrufen der Pakete: {e}")
            return []

    def _parse_aur_output(self, output):
        """Hilfsfunktion für spätere echte AUR-Ausgabe."""
        packages = []
        for line in output.splitlines():
            parts = line.split()
            if len(parts) >= 1:
                packages.append({
                    "name": parts[0],
                    "source": self.repo_name,
                    "description": "(keine Beschreibung verfügbar)"
                })
        return packages
