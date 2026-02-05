import sqlite3

DB_PATH = "db/finance.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Invoices table
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

    # Risk explanations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risk_explanations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            reason TEXT,
            FOREIGN KEY(invoice_id) REFERENCES invoices(id)
        )
    """)

    conn.commit()
    conn.close()
