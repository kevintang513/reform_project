import sqlite3
from datetime import datetime, UTC
from typing import List, Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

DATABASE_PATH = "invoices.db"

def init_database():
    """Initialize the database and create the invoices table if it doesn't exist"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            invoice_number TEXT,
            invoice_date TEXT,
            total_amount REAL,
            ct_number TEXT,
            mot TEXT,
            office TEXT,
            direction TEXT,
            calculated_code INTEGER,
            created_at TEXT NOT NULL,
            raw_json TEXT NOT NULL
        )
    """)

    # Create index on invoice_number for faster lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_invoice_number
        ON invoices(invoice_number)
    """)

    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

def save_invoice(invoice_data: Dict[str, Any]) -> int:
    """
    Save invoice data to the database

    Args:
        invoice_data: Dictionary containing invoice information

    Returns:
        The ID of the inserted record
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    created_at = datetime.now(UTC).isoformat()
    raw_json = json.dumps(invoice_data)

    cursor.execute("""
        INSERT INTO invoices (
            file_name, invoice_number, invoice_date, total_amount,
            ct_number, mot, office, direction, calculated_code,
            created_at, raw_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        invoice_data.get("file_name"),
        invoice_data.get("invoice_number"),
        invoice_data.get("invoice_date"),
        invoice_data.get("total_amount"),
        invoice_data.get("ct_number"),
        invoice_data.get("mot"),
        invoice_data.get("office"),
        invoice_data.get("direction"),
        invoice_data.get("calculated_code"),
        created_at,
        raw_json
    ))

    record_id = cursor.lastrowid
    conn.commit()
    conn.close()

    logger.info(f"Saved invoice {invoice_data.get('invoice_number')} with ID {record_id}")
    return record_id

def get_all_invoices(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Retrieve all invoices from the database

    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip

    Returns:
        List of invoice dictionaries
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM invoices
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

def get_invoice_by_number(invoice_number: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific invoice by invoice number

    Args:
        invoice_number: The invoice number to search for

    Returns:
        Invoice dictionary or None if not found
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM invoices
        WHERE invoice_number = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (invoice_number,))

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None

def get_invoice_count() -> int:
    """Get total count of invoices in the database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM invoices")
    count = cursor.fetchone()[0]

    conn.close()
    return count

def delete_invoice(invoice_id: int) -> bool:
    """
    Delete an invoice by ID

    Args:
        invoice_id: The ID of the invoice to delete

    Returns:
        True if deleted, False if not found
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
    deleted = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return deleted
