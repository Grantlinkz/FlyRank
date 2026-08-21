import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:dev@localhost:5432/tasks")

INITIAL_TASKS = [
    ("Learn HTTP & REST basics", True),
    ("Build CRUD API with FastAPI", False),
    ("Test endpoints in Swagger UI", False),
]

def is_sqlite() -> bool:
    return DATABASE_URL.startswith("sqlite")

def get_db_connection():
    """Create and return a database connection based on DATABASE_URL (PostgreSQL or SQLite fallback)."""
    if is_sqlite():
        import sqlite3
        db_path = DATABASE_URL.replace("sqlite:///", "") if "sqlite:///" in DATABASE_URL else "tasks.db"
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    else:
        import psycopg
        from psycopg.rows import dict_row
        url = DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        conn = psycopg.connect(url, row_factory=dict_row, connect_timeout=3)
        return conn

def init_db() -> None:
    """Initialize database table and seed initial tasks only if the table is empty."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if is_sqlite():
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        done INTEGER NOT NULL DEFAULT 0
                    )
                """)
                cursor.execute("SELECT COUNT(*) FROM tasks")
                count = cursor.fetchone()[0]
                if count == 0:
                    cursor.executemany(
                        "INSERT INTO tasks (title, done) VALUES (?, ?)",
                        [(t[0], 1 if t[1] else 0) for t in INITIAL_TASKS]
                    )
                    conn.commit()
            else:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        done BOOLEAN NOT NULL DEFAULT FALSE
                    )
                """)
                cursor.execute("SELECT COUNT(*) FROM tasks")
                row = cursor.fetchone()
                count = row[0] if isinstance(row, tuple) else row["count"]
                if count == 0:
                    for title, done in INITIAL_TASKS:
                        cursor.execute(
                            "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                            (title, done)
                        )
                    conn.commit()
    except Exception as e:
        print(f"Notice: DB auto-init deferred until database connection is available ({e})")

def task_row_to_dict(row: Any) -> Dict[str, Any]:
    """Convert database row object/dict to standard API task dictionary."""
    if isinstance(row, dict):
        return {
            "id": row["id"],
            "title": row["title"],
            "done": bool(row["done"])
        }
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }

def get_all_tasks(done: Optional[bool] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve tasks with optional status filtering and title search query."""
    placeholder = "?" if is_sqlite() else "%s"
    like_op = "LIKE" if is_sqlite() else "ILIKE"
    
    query = "SELECT id, title, done FROM tasks WHERE 1=1"
    params: List[Any] = []
    
    if done is not None:
        query += f" AND done = {placeholder}"
        params.append(1 if is_sqlite() and done else (0 if is_sqlite() else done))
        
    if search and search.strip():
        query += f" AND title {like_op} {placeholder}"
        params.append(f"%{search.strip()}%")
        
    query += " ORDER BY id ASC"
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [task_row_to_dict(r) for r in rows]

def get_task_by_id(task_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a single task by ID or return None if not found."""
    placeholder = "?" if is_sqlite() else "%s"
    query = f"SELECT id, title, done FROM tasks WHERE id = {placeholder}"
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (task_id,))
        row = cursor.fetchone()
        return task_row_to_dict(row) if row else None

def create_task(title: str) -> Dict[str, Any]:
    """Insert a new task into the database and return the created task."""
    clean_title = title.strip()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if is_sqlite():
            cursor.execute("INSERT INTO tasks (title, done) VALUES (?, 0)", (clean_title,))
            conn.commit()
            new_id = cursor.lastrowid
            return get_task_by_id(new_id)
        else:
            cursor.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, FALSE) RETURNING id, title, done",
                (clean_title,)
            )
            row = cursor.fetchone()
            conn.commit()
            return task_row_to_dict(row)

def update_task(task_id: int, title: Optional[str] = None, done: Optional[bool] = None) -> Optional[Dict[str, Any]]:
    """Update title and/or done status of a task by ID."""
    existing = get_task_by_id(task_id)
    if not existing:
        return None
        
    new_title = title.strip() if title is not None else existing["title"]
    new_done = done if done is not None else existing["done"]
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if is_sqlite():
            cursor.execute(
                "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
                (new_title, 1 if new_done else 0, task_id)
            )
            conn.commit()
            return get_task_by_id(task_id)
        else:
            cursor.execute(
                "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done",
                (new_title, new_done, task_id)
            )
            row = cursor.fetchone()
            conn.commit()
            return task_row_to_dict(row) if row else None

def delete_task(task_id: int) -> bool:
    """Delete a task by ID. Return True if deleted, False if task did not exist."""
    existing = get_task_by_id(task_id)
    if not existing:
        return False
        
    placeholder = "?" if is_sqlite() else "%s"
    query = f"DELETE FROM tasks WHERE id = {placeholder}"
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (task_id,))
        conn.commit()
        return True

def get_task_stats() -> Dict[str, int]:
    """Compute task count statistics directly using SQL queries."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tasks")
        row_total = cursor.fetchone()
        total = row_total[0] if isinstance(row_total, tuple) else row_total["count"]
        
        done_query = "SELECT COUNT(*) FROM tasks WHERE done = 1" if is_sqlite() else "SELECT COUNT(*) FROM tasks WHERE done = TRUE"
        cursor.execute(done_query)
        row_done = cursor.fetchone()
        done_count = row_done[0] if isinstance(row_done, tuple) else row_done["count"]
        
        open_count = total - done_count
        return {"total": total, "done": done_count, "open": open_count}

def reset_db() -> List[Dict[str, Any]]:
    """Reset the tasks table and re-seed with default sample tasks."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks")
        if is_sqlite():
            cursor.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                [(t[0], 1 if t[1] else 0) for t in INITIAL_TASKS]
            )
        else:
            for title, done in INITIAL_TASKS:
                cursor.execute(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                    (title, done)
                )
        conn.commit()
        
    return get_all_tasks()
