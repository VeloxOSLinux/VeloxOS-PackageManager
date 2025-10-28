import subprocess

class FlathubRepo:
    """Flathub Repo - nur Name für Initialbefüllung."""

    def __init__(self):
        self.repo_name = "Flathub"

    def get_available_packages(self):
        try:
            output = subprocess.check_output(["flatpak", "remote-ls", "--app", "flathub"], text=True, stderr=subprocess.DEVNULL)
            packages = []
            for line in output.splitlines():
                packages.append({
                    "name": line.strip(),
                    "source": self.repo_name,
                    "version": "",
                    "description": ""
                })
            return packages
        except subprocess.CalledProcessError:
            return []
