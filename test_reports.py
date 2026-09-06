"""
Comprehensive automated tests for Milestone W7b (Assignment A8: PDF Report Generator).
Covers:
- Stage 1: Idempotent dataset seeding (60 books).
- Stage 2: Pure SQL aggregation calculations and mathematical invariants.
- Stage 3: HTML template print CSS defenses and Playwright PDF rendering.
- Stage 4: Store & Link API endpoints (POST 201, GET metadata, GET binary file stream).
- Stage 5: Idempotency protection (POST 200 on duplicate request, force regeneration).
"""

import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from main import app
from src.reports.database import init_report_db, get_report_db_connection, DB_PATH, REPORTS_DIR
from src.reports.seed import seed_books
from src.reports.queries import get_report_data
from src.reports.template import generate_report_html
from src.reports.renderer import render_pdf_sync


@pytest.fixture(scope="module", autouse=True)
def setup_reports_env():
    """Ensure database and seed data are ready before tests run."""
    init_report_db()
    seed_books()
    yield


def test_stage1_idempotent_seeding():
    """Test that seeding twice results in exactly 60 records."""
    count1 = seed_books()
    count2 = seed_books()
    assert count1 == 60
    assert count2 == 60

    with get_report_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM books")
        total = cursor.fetchone()[0]
        assert total == 60


def test_stage2_sql_aggregations():
    """Test SQL aggregation calculations and invariants."""
    data = get_report_data()

    assert data["total_books"] == 60
    assert data["average_price"] > 0
    assert len(data["top_5"]) == 5
    assert len(data["rating_breakdown"]) == 5
    assert len(data["all_books"]) == 60

    # Invariant: ratings sum equals total books
    sum_ratings = sum(item["count"] for item in data["rating_breakdown"])
    assert sum_ratings == 60

    # Invariant: top 5 prices are sorted in descending order
    prices = [b["price"] for b in data["top_5"]]
    assert prices == sorted(prices, reverse=True)
    assert prices[0] <= data["max_price"]


def test_stage3_html_template_and_print_css():
    """Verify defensive print CSS rules in HTML output."""
    data = get_report_data()
    html = generate_report_html(data)

    assert "FlyRank Intelligence" in html
    assert "@page" in html
    assert "break-inside: avoid;" in html
    assert "<thead>" in html
    assert "Slow States of Collapse: Poems" in html
    assert len(html) > 5000


def test_stage3_playwright_pdf_rendering(tmp_path):
    """Verify headless Chromium renders a valid PDF with multiple pages."""
    data = get_report_data()
    html = generate_report_html(data)
    test_pdf = tmp_path / "test_output.pdf"

    out_path = render_pdf_sync(html, test_pdf)
    assert Path(out_path).exists()

    with open(out_path, "rb") as f:
        header = f.read(5)
        # PDF magic bytes
        assert header == b"%PDF-"
        f.seek(0)
        content = f.read()
        # Ensure multi-page markers (/Type /Page) appear >= 2 times
        page_count = content.count(b"/Type /Page") - content.count(b"/Type /Pages")
        assert page_count >= 2


def test_stage4_api_generate_and_serve_by_link():
    """Verify POST /reports returns 201 with file link, and GET /reports/:id/file streams binary PDF."""
    client = TestClient(app)

    # Force generate a fresh report
    res_post = client.post("/reports", json={"force": True})
    assert res_post.status_code == 201
    post_data = res_post.json()
    assert "id" in post_data
    assert "file" in post_data
    assert post_data["file"] == f"/reports/{post_data['id']}/file"
    report_id = post_data["id"]

    # GET /reports/{id} metadata endpoint
    res_get = client.get(f"/reports/{report_id}")
    assert res_get.status_code == 200
    get_data = res_get.json()
    assert get_data["id"] == report_id
    assert "created_at" in get_data
    assert get_data["file"] == f"/reports/{report_id}/file"

    # GET /reports/{id}/file binary stream endpoint
    res_file = client.get(f"/reports/{report_id}/file")
    assert res_file.status_code == 200
    assert res_file.headers["content-type"] == "application/pdf"
    assert res_file.content.startswith(b"%PDF-")
    assert len(res_file.content) > 10000


def test_stage5_idempotency_protection():
    """Verify rapid consecutive requests return existing report with 200 OK."""
    client = TestClient(app)

    # First request: ensure we have today's report
    res1 = client.post("/reports", json={"force": True})
    assert res1.status_code == 201
    id1 = res1.json()["id"]

    # Second request without force: should return 200 OK with same ID
    res2 = client.post("/reports")
    assert res2.status_code == 200
    id2 = res2.json()["id"]
    assert id1 == id2

    # Third request with force=True: should generate a new report with 201 Created
    res3 = client.post("/reports", json={"force": True})
    assert res3.status_code == 201
    id3 = res3.json()["id"]
    assert id3 > id1


def test_404_handling_unknown_report():
    """Verify unknown report ID returns 404 Not Found."""
    client = TestClient(app)
    res_meta = client.get("/reports/999999")
    assert res_meta.status_code == 404

    res_file = client.get("/reports/999999/file")
    assert res_file.status_code == 404
