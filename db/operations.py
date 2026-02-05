from db.database import get_connection


def insert_invoice(invoice):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO invoices (
            source_file, bill_number, invoice_date,
            subtotal, tax_amount, grand_total,
            confidence, risk
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        invoice.get("source_file"),
        invoice.get("bill_number"),
        invoice.get("invoice_date"),
        invoice.get("subtotal"),
        invoice.get("tax_amount"),
        invoice.get("grand_total"),
        invoice.get("confidence"),
        invoice.get("risk")
    ))

    invoice_id = cursor.lastrowid

    # Insert risk explanations
    for reason in invoice.get("risk_explanation", []):
        cursor.execute("""
            INSERT INTO risk_explanations (invoice_id, reason)
            VALUES (?, ?)
        """, (invoice_id, reason))

    conn.commit()
    conn.close()

def get_all_invoices():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT source_file, bill_number, invoice_date,
               subtotal, tax_amount, grand_total,
               confidence, risk
        FROM invoices
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_high_risk_invoices():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT source_file, bill_number, invoice_date,
               grand_total, confidence, risk
        FROM invoices
        WHERE risk = 'high'
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows
