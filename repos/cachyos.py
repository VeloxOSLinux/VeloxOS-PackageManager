import subprocess

class CachyOSRepo:
    """CachyOS Repo - nur Name und Version für Initialbefüllung."""

    def __init__(self):
        self.repo_name = "CachyOS Repo"

    def get_available_packages(self):
        try:
            output = subprocess.check_output(["pacman", "-Sl", "cachyos"], text=True, stderr=subprocess.DEVNULL)
            packages = []
            for line in output.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    packages.append({
                        "name": parts[1],
                        "source": self.repo_name,
                        "version": "(unbekannt)",  # Optional Version
                        "description": ""  # Lazy loading
                    })
            return packages
        except subprocess.CalledProcessError:
            return []
