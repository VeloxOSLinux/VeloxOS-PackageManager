import subprocess
import shutil

class AURRepo:
    """AUR Repo via yay - nur Paketnamen für Initialbefüllung."""

    def __init__(self):
        self.repo_name = "AUR"

    def get_available_packages(self):
        if not shutil.which("yay"):
            return []
        try:
            output = subprocess.check_output(["yay", "-Ssq"], text=True, stderr=subprocess.DEVNULL)
            return [{"name": name.strip(), "source": self.repo_name, "version": "", "description": ""} for name in output.splitlines()]
        except subprocess.CalledProcessError:
            return []
