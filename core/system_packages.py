import subprocess

def get_installed_packages():
    """Liefert alle installierten Pakete aus Pacman & AUR als Liste von Dicts."""
    packages = []

    # --- Pacman / CachyOS Repo ---
    try:
        output = subprocess.check_output(["pacman", "-Q"], text=True)
        for line in output.splitlines():
            name, version = line.split()[:2]
            packages.append({"name": name, "source": "CachyOS Repo", "version": version, "description": ""})
    except Exception:
        pass

    # --- AUR ---
    for helper in ["yay", "paru", "trizen"]:
        if subprocess.call(["which", helper], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            try:
                output = subprocess.check_output([helper, "-Q"], text=True)
                for line in output.splitlines():
                    name, version = line.split()[:2]
                    packages.append({"name": name, "source": "AUR", "version": version, "description": ""})
            except Exception:
                pass
            break

    return packages
