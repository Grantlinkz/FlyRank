"""
Reports module for Milestone W7b (Assignment A8).
Implements the Store and Link PDF Report Generator.
"""

from .database import get_report_db_connection, init_report_db, DB_PATH
from .seed import seed_books
from .queries import get_report_data
from .template import generate_report_html
from .renderer import render_pdf, render_pdf_sync

__all__ = [
    "get_report_db_connection",
    "init_report_db",
    "DB_PATH",
    "seed_books",
    "get_report_data",
    "generate_report_html",
    "render_pdf",
    "render_pdf_sync",
]
