import sqlite3

DB_PATH = "db/finance.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 👈 Yeh add karo — dict jaisa return karega
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Invoices table (same as before)
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

    # Risk explanations table (same as before)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risk_explanations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            reason TEXT,
            FOREIGN KEY(invoice_id) REFERENCES invoices(id)
        )
    """)

    # 👇 Users table — yahan add kiya init_db ke andar
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT UNIQUE NOT NULL,
            email      TEXT UNIQUE NOT NULL,
            password   TEXT NOT NULL,
            role       TEXT DEFAULT 'user',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()