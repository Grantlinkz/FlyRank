import sqlite3
from pathlib import Path

# Database file location in the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = PROJECT_ROOT / "report.db"
REPORTS_DIR = PROJECT_ROOT / "reports"


def get_report_db_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Return a SQLite connection with row factory configured."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_report_db(db_path: Path = DB_PATH) -> None:
    """Initialize SQLite schema for books and reports bookkeeping."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with get_report_db_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                price REAL NOT NULL,
                rating INTEGER NOT NULL,
                url TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)
        conn.commit()


if __name__ == "__main__":
    init_report_db()
    print(f"Initialized report.db at {DB_PATH}")
