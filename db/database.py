import os
import sqlite3
from sqlite3 import Row

DATABASE_PATH = os.environ.get("DATABASE_PATH", "db/finance.db")


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_file TEXT,
            bill_number TEXT,
            invoice_date TEXT,
            subtotal REAL,
            tax_amount REAL,
            grand_total REAL,
            confidence REAL,
            risk TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risk_explanations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            reason TEXT,
            FOREIGN KEY(invoice_id) REFERENCES invoices(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT UNIQUE NOT NULL,
            email      TEXT UNIQUE NOT NULL,
            password   TEXT NOT NULL,
            role       TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
