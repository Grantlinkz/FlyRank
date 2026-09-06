from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List
from .database import get_report_db_connection, init_report_db, REPORTS_DIR, DB_PATH
from .queries import get_report_data
from .template import generate_report_html
from .renderer import render_pdf, render_pdf_sync


def get_report_record(report_id: int, db_path: Path = DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieve metadata for a specific PDF report by its integer ID."""
    with get_report_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, path, created_at FROM reports WHERE id = ?", (report_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": int(row["id"]),
            "path": row["path"],
            "created_at": row["created_at"],
            "file": f"/reports/{row['id']}/file",
        }


def get_today_report(db_path: Path = DB_PATH) -> Optional[Dict[str, Any]]:
    """
    Idempotency check: Find if a report has already been generated today.
    Uses SQLite's DATE(created_at) = DATE('now') function.
    """
    with get_report_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, path, created_at 
            FROM reports 
            WHERE DATE(created_at) = DATE('now')
            ORDER BY id DESC 
            LIMIT 1
        """)
        row = cursor.fetchone()
        if not row:
            return None
        file_path = Path(row["path"])
        # If the file physically exists on disk, we can reuse it
        if file_path.exists():
            return {
                "id": int(row["id"]),
                "path": row["path"],
                "created_at": row["created_at"],
                "file": f"/reports/{row['id']}/file",
            }
        return None


def get_all_pdf_reports(db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    """Return all recorded PDF reports for listing and dashboard views."""
    init_report_db(db_path)
    with get_report_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, path, created_at FROM reports ORDER BY id DESC")
        rows = cursor.fetchall()
        return [
            {
                "id": int(r["id"]),
                "path": r["path"],
                "created_at": r["created_at"],
                "file": f"/reports/{r['id']}/file",
            }
            for r in rows
        ]


async def create_pdf_report(db_path: Path = DB_PATH) -> Dict[str, Any]:
    """
    Full pipeline execution:
    1. Query SQL aggregates
    2. Render HTML template with print CSS
    3. Render PDF via Playwright
    4. Store in reports/<id>.pdf and record metadata in SQLite reports table
    """
    init_report_db(db_path)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Query metrics
    report_data = get_report_data(db_path)

    # 2. Allocate DB record ID
    created_at_dt = datetime.now()
    created_at_iso = created_at_dt.isoformat()

    with get_report_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO reports (path, created_at) VALUES (?, ?)", ("", created_at_iso))
        report_id = cursor.lastrowid
        pdf_path = REPORTS_DIR / f"{report_id}.pdf"
        cursor.execute("UPDATE reports SET path = ? WHERE id = ?", (str(pdf_path), report_id))
        conn.commit()

    # 3. Render HTML
    html_content = generate_report_html(report_data, generated_at=created_at_dt)

    # 4. Render PDF to disk via Playwright
    await render_pdf(html_content, pdf_path)

    return {
        "id": report_id,
        "path": str(pdf_path),
        "created_at": created_at_iso,
        "file": f"/reports/{report_id}/file",
    }


async def generate_or_get_report(force: bool = False, db_path: Path = DB_PATH) -> Tuple[Dict[str, Any], bool]:
    """
    Stage 5 Idempotency Guard:
    If a report was already created today and force is False, return existing report (created=False).
    Otherwise, generate fresh report (created=True).
    """
    if not force:
        existing = get_today_report(db_path)
        if existing:
            return existing, False

    new_report = await create_pdf_report(db_path)
    return new_report, True
