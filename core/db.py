import sqlite3
import os
from repos.veloxos import VeloxOSRepo
from repos.flathub import FlathubRepo
from repos.aur import AURRepo

# --- NEUE PFAD-LOGIK FÜR SYSTEM-INSTALLATION ---
# Wir speichern die DB im Home-Verzeichnis des Nutzers,
# da /usr/share/ schreibgeschützt ist.
HOME = os.path.expanduser("~")
DB_DIR = os.path.join(HOME, ".local", "share", "velox-package-manager")
DB_PATH = os.path.join(DB_DIR, "velox_packages.db")


def get_connection():
    """Stellt sicher, dass der Ordner existiert und liefert die Verbindung."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR, exist_ok=True)
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

    # Migration: Falls icon_url fehlt
    try:
        cursor.execute("SELECT icon_url FROM packages LIMIT 1")
    except sqlite3.OperationalError:
        print("[DB] Erweitere Schema um icon_url...")
        cursor.execute("ALTER TABLE packages ADD COLUMN icon_url TEXT")

    # Standard-Status setzen (Namen an VeloxOS angepasst)
    for repo in ["Flathub", "AUR", "VeloxOS Repo"]:
        cursor.execute("INSERT OR IGNORE INTO repo_status (repo_name, enabled) VALUES (?, ?)", (repo, 0))

    # Prüfung: Sind Daten vorhanden?
    cursor.execute("SELECT COUNT(*) FROM packages")
    count = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    if count == 0:
        print("[DB] Datenbank leer. Starte Erstbefüllung im Hintergrund...")
        populate_initial_packages()
    else:
        print(f"[DB] {count} Pakete bereits in DB unter {DB_PATH} vorhanden.")


def populate_initial_packages():
    """Lädt Pakete von allen Repos und speichert sie effizient."""
    conn = get_connection()
    cursor = conn.cursor()

    # Wichtig: Hier die Klassen nutzen, die du in den Repos definiert hast
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


def get_package_data(repo_name: str, package_name: str) -> dict:
    """Liefert alle Paketdetails als Dictionary für die Detail-Ansicht."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row  # Erlaubt Zugriff via Key (row['version'])
    cursor = conn.cursor()
    cursor.execute(
        "SELECT version, description, icon_url FROM packages WHERE repo_name = ? AND package_name = ?",
        (repo_name, package_name)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return {"version": "Unbekannt", "description": "Keine Daten in lokaler DB.", "icon_url": ""}