import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id SERIAL PRIMARY KEY,
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
            id SERIAL PRIMARY KEY,
            invoice_id INTEGER,
            reason TEXT,
            FOREIGN KEY(invoice_id) REFERENCES invoices(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         SERIAL PRIMARY KEY,
            username   TEXT UNIQUE NOT NULL,
            email      TEXT UNIQUE NOT NULL,
            password   TEXT NOT NULL,
            role       TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
