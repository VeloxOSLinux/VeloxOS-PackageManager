import sqlite3
import os
from repos.cachyos import CachyOSRepo
from repos.flathub import FlathubRepo
from repos.aur import AURRepo

DB_PATH = os.path.join(os.path.dirname(__file__), "cachy_package_manager.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    """Erstellt Tabellen, falls sie noch nicht existieren."""
    conn = get_connection()
    cursor = conn.cursor()

    # Repo-Status
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS repo_status (
        repo_name TEXT PRIMARY KEY,
        enabled INTEGER
    )
    """)

    # Paket-Tabelle
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS packages (
        repo_name TEXT,
        package_name TEXT,
        version TEXT,
        description TEXT,
        PRIMARY KEY (repo_name, package_name)
    )
    """)

    # Dummy Repo-Status falls nicht vorhanden
    for repo in ["flathub", "aur", "CachyOS Repo"]:
        cursor.execute("INSERT OR IGNORE INTO repo_status (repo_name, enabled) VALUES (?, ?)", (repo, 0))

    conn.commit()
    conn.close()

def populate_initial_packages():
    """Füllt die DB beim ersten Start mit allen verfügbaren Paketen inkl. Beschreibung."""
    conn = get_connection()
    cursor = conn.cursor()

    repos = [
        CachyOSRepo(),
        FlathubRepo(),
        AURRepo()
    ]

    for repo in repos:
        try:
            packages = repo.get_available_packages()
            for pkg in packages:
                name = pkg.get("name")
                version = pkg.get("version", "")
                desc = pkg.get("description", "")
                cursor.execute("""
                    INSERT OR REPLACE INTO packages (repo_name, package_name, version, description)
                    VALUES (?, ?, ?, ?)
                """, (repo.repo_name, name, version, desc))
        except Exception as e:
            print(f"[DB] Fehler beim Befüllen von {repo.repo_name}: {e}")

    conn.commit()
    conn.close()

# ------------------------------

def get_repo_status(repo_name: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT enabled FROM repo_status WHERE repo_name = ?", (repo_name,))
    row = cursor.fetchone()
    conn.close()
    return bool(row[0]) if row else False

def set_repo_status(repo_name: str, enabled: bool):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO repo_status (repo_name, enabled) VALUES (?, ?)", (repo_name, int(enabled)))
    conn.commit()
    conn.close()

def get_package_description(repo_name: str, package_name: str) -> str:
    """Liefert die Beschreibung eines Pakets aus der DB."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT description FROM packages WHERE repo_name = ? AND package_name = ?",
        (repo_name, package_name)
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else ""
