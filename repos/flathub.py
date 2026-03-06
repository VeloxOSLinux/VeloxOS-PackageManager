import requests


class FlathubRepo:
    """Flathub Repo - unterstützt Massen-Scans und gezieltes Lazy Loading."""

    def __init__(self):
        self.repo_name = "Flathub"
        self.api_url_list = "https://flathub.org/api/v2/appstream"
        self.api_url_detail = "https://flathub.org/api/v2/appstream/"  # + ID

    def get_available_packages(self):
        """Holt die Basis-Liste (IDs)."""
        try:
            response = requests.get(self.api_url_list, timeout=10)
            response.raise_for_status()
            app_ids = response.json()

            packages = []
            for app_id in app_ids:
                packages.append({
                    "name": app_id,
                    "source": self.repo_name,
                    "version": "latest",
                    "description": "Flathub Application (Klicken für Details)",
                    "icon_url": f"https://dl.flathub.org/repo/appstream/x86_64/icons/128x128/{app_id}.png"
                })
            return packages
        except Exception as e:
            print(f"Fehler beim Abrufen der Flathub-Liste: {e}")
            return []

    def get_package_details(self, app_id):
        """Lazy Loading: Holt detaillierte Infos für eine spezifische App."""
        try:
            url = f"{self.api_url_detail}{app_id}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Wir extrahieren die Beschreibung und Version
                return {
                    "description": data.get("description", "Keine Beschreibung verfügbar."),
                    "version": data.get("version", "latest"),
                    "name_pretty": data.get("name", app_id)
                }
        except Exception as e:
            print(f"Fehler beim Lazy Loading für {app_id}: {e}")
        return None