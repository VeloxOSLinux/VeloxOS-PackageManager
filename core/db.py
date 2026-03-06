import sqlite3
import os
from repos.veloxos import VeloxOSRepo
from repos.flathub import FlathubRepo
from repos.aur import AURRepo

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "cachy_package_manager.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    """Erstellt Tabellen und prüft auf Erstbefüllung."""
    conn = get_connection()
    cursor = conn.cursor()

    # Repo-Status Tabelle
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
        icon_url TEXT,
        PRIMARY KEY (repo_name, package_name)
    )
    """)

    # Migration: Falls icon_url fehlt (in existierenden DBs)
    try:
        cursor.execute("SELECT icon_url FROM packages LIMIT 1")
    except sqlite3.OperationalError:
        print("[DB] Erweitere Schema um icon_url...")
        cursor.execute("ALTER TABLE packages ADD COLUMN icon_url TEXT")

    # Standard-Status setzen
    for repo in ["Flathub", "AUR", "CachyOS Repo"]:
        cursor.execute("INSERT OR IGNORE INTO repo_status (repo_name, enabled) VALUES (?, ?)", (repo, 0))

    # Prüfung: Sind Daten vorhanden?
    cursor.execute("SELECT COUNT(*) FROM packages")
    count = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    if count == 0:
        print("[DB] Datenbank leer. Starte Erstbefüllung...")
        populate_initial_packages()
    else:
        print(f"[DB] {count} Pakete bereits in DB vorhanden.")


def populate_initial_packages():
    """Lädt Pakete von allen Repos und speichert sie effizient."""
    conn = get_connection()
    cursor = conn.cursor()

    repos = [VeloxOSRepo(), FlathubRepo(), AURRepo()]

    for repo in repos:
        try:
            print(f"[DB] Lade Daten von {repo.repo_name}...")
            packages = repo.get_available_packages()

            # Massen-Insert vorbereiten
            data_to_insert = []
            for p in packages:
                data_to_insert.append((
                    repo.repo_name,
                    p.get("name"),
                    p.get("version", ""),
                    p.get("description", ""),
                    p.get("icon_url", "")
                ))

            cursor.executemany("""
                INSERT OR REPLACE INTO packages (repo_name, package_name, version, description, icon_url)
                VALUES (?, ?, ?, ?, ?)
            """, data_to_insert)

            print(f"[DB] {len(data_to_insert)} Pakete von {repo.repo_name} gespeichert.")
        except Exception as e:
            print(f"[DB] Fehler bei {repo.repo_name}: {e}")

    conn.commit()
    conn.close()


# --- Hilfsfunktionen für die GUI ---

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
    """Wird von PackageDetailWidget benötigt."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT description FROM packages WHERE repo_name = ? AND package_name = ?",
        (repo_name, package_name)
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else ""


def get_package_data(repo_name: str, package_name: str) -> dict:
    """Liefert alle Paketdetails als Dictionary."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT version, description, icon_url FROM packages WHERE repo_name = ? AND package_name = ?",
        (repo_name, package_name)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {"version": "", "description": "", "icon_url": ""}