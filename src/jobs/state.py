"""
In-memory state management for asynchronous reports.
Implements the in-memory data store specified for Milestone W7.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone
import uuid

# In-memory dictionary storing reports by unique ID: {id: report_dict}
reports_db: Dict[str, Dict[str, Any]] = {}


def generate_report_id() -> str:
    """Generate a clean unique report ID prefixed with 'rep_'."""
    return f"rep_{uuid.uuid4().hex[:8]}"


def create_report(topic: str, report_id: Optional[str] = None) -> Dict[str, Any]:
    """Initialize and persist a new report record in memory."""
    rid = report_id or generate_report_id()
    now_iso = datetime.now(timezone.utc).isoformat()
    record = {
        "id": rid,
        "topic": topic,
        "status": "pending",
        "result": None,
        "created_at": now_iso,
        "attempts": 0,
    }
    reports_db[rid] = record
    return record


def get_report(report_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a report record by ID, or None if not found."""
    return reports_db.get(report_id)


def update_report(
    report_id: str,
    status: str,
    result: Optional[str] = None,
    error: Optional[str] = None,
    attempts: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """Update status, result, and attempts for an existing report."""
    if report_id not in reports_db:
        return None

    record = reports_db[report_id]
    record["status"] = status
    if result is not None:
        record["result"] = result
    if error is not None:
        record["error"] = error
    if attempts is not None:
        record["attempts"] = attempts

    return record


def get_all_reports() -> list[Dict[str, Any]]:
    """Retrieve all reports in descending order of creation."""
    return list(reports_db.values())


def get_report_counts() -> Dict[str, int]:
    """Calculate summary count of reports by status for heartbeat cron."""
    counts = {"pending": 0, "done": 0, "failed": 0, "total": len(reports_db)}
    for r in reports_db.values():
        st = r.get("status")
        if st in counts:
            counts[st] += 1
    return counts


def reset_reports_db() -> None:
    """Clear all reports (useful for test isolation)."""
    reports_db.clear()
