import sqlite3
import os

# Pfad zur DB (im Projekt, alternativ Home-Ordner)
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

    # Dummy-Paket-Tabelle
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS packages (
        repo_name TEXT,
        package_name TEXT,
        version TEXT,
        description TEXT,
        PRIMARY KEY (repo_name, package_name)
    )
    """)

    # Dummy-Daten, falls noch nicht vorhanden
    for repo in ["flathub", "aur"]:
        cursor.execute("INSERT OR IGNORE INTO repo_status (repo_name, enabled) VALUES (?, ?)", (repo, 0))

    dummy_packages = [
        ("flathub", "vlc", "3.0.16", "Media Player"),
        ("aur", "yay", "11.0.2", "AUR Helper")
    ]
    for pkg in dummy_packages:
        cursor.execute("""
        INSERT OR IGNORE INTO packages (repo_name, package_name, version, description)
        VALUES (?, ?, ?, ?)
        """, pkg)

    conn.commit()
    conn.close()

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
