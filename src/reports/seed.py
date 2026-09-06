import json
from pathlib import Path
from .database import get_report_db_connection, init_report_db, PROJECT_ROOT, DB_PATH

BOOKS_JSON_PATH = PROJECT_ROOT / "scraper" / "output" / "books.json"

RATING_MAP = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}


def parse_rating(rating_val) -> int:
    """Safely convert text or numeric rating to integer 1-5."""
    if isinstance(rating_val, int):
        return max(1, min(5, rating_val))
    if isinstance(rating_val, str):
        cleaned = rating_val.strip().lower()
        if cleaned in RATING_MAP:
            return RATING_MAP[cleaned]
        if cleaned.isdigit():
            return int(cleaned)
    return 3  # Neutral fallback


def seed_books(db_path: Path = DB_PATH, source_json: Path = BOOKS_JSON_PATH) -> int:
    """
    Idempotently seeds the 'books' table in report.db.
    Clears existing rows first to ensure consecutive executions do not duplicate data.
    """
    init_report_db(db_path)

    if not source_json.exists():
        raise FileNotFoundError(f"Source books JSON not found at {source_json}")

    with open(source_json, "r", encoding="utf-8") as f:
        books_data = json.load(f)

    with get_report_db_connection(db_path) as conn:
        cursor = conn.cursor()
        # Idempotency defense: delete existing rows
        cursor.execute("DELETE FROM books")

        records_to_insert = []
        for item in books_data:
            title = item.get("title", "").strip()
            price = float(item.get("price_gbp", 0.0))
            rating = parse_rating(item.get("rating_text", ""))
            url = item.get("product_url", "").strip()
            records_to_insert.append((title, price, rating, url))

        cursor.executemany(
            "INSERT INTO books (title, price, rating, url) VALUES (?, ?, ?, ?)",
            records_to_insert,
        )
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM books")
        count = cursor.fetchone()[0]
        return count


if __name__ == "__main__":
    count = seed_books()
    print(f"Seeding complete. Total books in report.db: {count}")
