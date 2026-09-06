"""
Reports module for Milestone W7b (Assignment A8).
Implements the Store and Link PDF Report Generator.
"""

from .database import get_report_db_connection, init_report_db, DB_PATH
from .seed import seed_books
from .queries import get_report_data

__all__ = [
    "get_report_db_connection",
    "init_report_db",
    "DB_PATH",
    "seed_books",
    "get_report_data",
]
