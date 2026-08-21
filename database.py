import sqlite3
from typing import Optional, List, Dict, Any

DB_FILE = "tasks.db"

INITIAL_TASKS = [
    ("Learn HTTP & REST basics", 1),
    ("Build CRUD API with FastAPI", 0),
    ("Test endpoints in Swagger UI", 0),
]

def get_db_connection() -> sqlite3.Connection:
    """Create and return a database connection with dictionary-like row access."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Initialize database table and seed initial tasks only if the table is empty."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
        """)
        
        # Check row count for seed-once rule
        cursor.execute("SELECT COUNT(*) FROM tasks")
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                INITIAL_TASKS
            )
            conn.commit()

def task_row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert a SQLite Row object to a standard task dictionary with boolean `done`."""
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }

def get_all_tasks(done: Optional[bool] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve tasks with optional status filtering and title search query."""
    query = "SELECT id, title, done FROM tasks WHERE 1=1"
    params: List[Any] = []
    
    if done is not None:
        query += " AND done = ?"
        params.append(1 if done else 0)
        
    if search and search.strip():
        query += " AND title LIKE ?"
        params.append(f"%{search.strip()}%")
        
    query += " ORDER BY id ASC"
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [task_row_to_dict(r) for r in rows]

def get_task_by_id(task_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a single task by ID or return None if not found."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        return task_row_to_dict(row) if row else None

def create_task(title: str) -> Dict[str, Any]:
    """Insert a new task into the database and return the inserted task."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, done) VALUES (?, 0)",
            (title.strip(),)
        )
        conn.commit()
        new_id = cursor.lastrowid
        
    return get_task_by_id(new_id)

def update_task(task_id: int, title: Optional[str] = None, done: Optional[bool] = None) -> Optional[Dict[str, Any]]:
    """Update title and/or done status of a task by ID."""
    existing = get_task_by_id(task_id)
    if not existing:
        return None
        
    new_title = title.strip() if title is not None else existing["title"]
    new_done = (1 if done else 0) if done is not None else (1 if existing["done"] else 0)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (new_title, new_done, task_id)
        )
        conn.commit()
        
    return get_task_by_id(task_id)

def delete_task(task_id: int) -> bool:
    """Delete a task by ID. Return True if deleted, False if task did not exist."""
    existing = get_task_by_id(task_id)
    if not existing:
        return False
        
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return True

def get_task_stats() -> Dict[str, int]:
    """Compute task count statistics directly using SQL queries."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tasks")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE done = 1")
        done_count = cursor.fetchone()[0]
        
        open_count = total - done_count
        return {"total": total, "done": done_count, "open": open_count}

def reset_db() -> List[Dict[str, Any]]:
    """Reset the tasks table and re-seed with default sample tasks."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks")
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            INITIAL_TASKS
        )
        conn.commit()
        
    return get_all_tasks()
