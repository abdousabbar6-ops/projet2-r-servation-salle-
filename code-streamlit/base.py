import sqlite3
from pathlib import Path

RACINE = Path(__file__).parent.parent
BASE = RACINE / "data.db"


def ouvrir_base():
    """Ouvre la base et la crée au premier lancement. Inutile de modifier cette fonction."""
    neuve = not BASE.exists()
    conn = sqlite3.connect(BASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    if neuve:
        conn.executescript((RACINE / "base.sql").read_text(encoding="utf-8"))
    return conn
