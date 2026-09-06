from typing import Dict, Any, List
from pathlib import Path
from .database import get_report_db_connection, DB_PATH


def get_report_data(db_path: Path = DB_PATH) -> Dict[str, Any]:
    """
    Executes pure SQL aggregation queries to construct the report dataset.
    Returns:
        total_books: Total count of books
        average_price: Average price rounded to 2 decimal places
        total_value: Total value of inventory
        top_5: Top 5 most expensive books
        rating_breakdown: Distribution of books per star rating (1-5)
        all_books: All books for multi-page document generation
    """
    with get_report_db_connection(db_path) as conn:
        cursor = conn.cursor()

        # 1. Total count
        cursor.execute("SELECT COUNT(*) FROM books")
        total_books = cursor.fetchone()[0]

        # 2. Average price and total inventory value
        cursor.execute("SELECT ROUND(AVG(price), 2), ROUND(SUM(price), 2), ROUND(MIN(price), 2), ROUND(MAX(price), 2) FROM books")
        row = cursor.fetchone()
        avg_price = float(row[0]) if row[0] is not None else 0.0
        total_value = float(row[1]) if row[1] is not None else 0.0
        min_price = float(row[2]) if row[2] is not None else 0.0
        max_price = float(row[3]) if row[3] is not None else 0.0

        # 3. Top 5 most expensive books
        cursor.execute(
            "SELECT title, price, rating, url FROM books ORDER BY price DESC LIMIT 5"
        )
        top_5 = [
            {
                "title": r["title"],
                "price": float(r["price"]),
                "rating": int(r["rating"]),
                "url": r["url"],
            }
            for r in cursor.fetchall()
        ]

        # 4. Number of books per star rating
        cursor.execute(
            "SELECT rating, COUNT(*) as count FROM books GROUP BY rating ORDER BY rating DESC"
        )
        rating_breakdown = [
            {"rating": int(r["rating"]), "count": int(r["count"])}
            for r in cursor.fetchall()
        ]

        # 5. Complete catalog for multi-page print document
        cursor.execute(
            "SELECT id, title, price, rating, url FROM books ORDER BY id ASC"
        )
        all_books = [
            {
                "id": int(r["id"]),
                "title": r["title"],
                "price": float(r["price"]),
                "rating": int(r["rating"]),
                "url": r["url"],
            }
            for r in cursor.fetchall()
        ]

    # Mathematical consistency sanity checks
    sum_ratings = sum(item["count"] for item in rating_breakdown)
    if total_books > 0:
        assert sum_ratings == total_books, f"Rating sum ({sum_ratings}) != Total books ({total_books})"
        if top_5:
            assert top_5[0]["price"] <= max_price + 0.001

    return {
        "total_books": total_books,
        "average_price": avg_price,
        "total_value": total_value,
        "min_price": min_price,
        "max_price": max_price,
        "top_5": top_5,
        "rating_breakdown": rating_breakdown,
        "all_books": all_books,
    }


if __name__ == "__main__":
    import json
    data = get_report_data()
    # Print summary without all 60 rows for clean terminal preview
    preview = {k: v for k, v in data.items() if k != "all_books"}
    preview["all_books_count"] = len(data["all_books"])
    print(json.dumps(preview, indent=2))
