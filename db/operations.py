import sqlite3
from db.database import get_connection


# -------------------------
# Insert Invoice
# -------------------------
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


# -------------------------
# Get All Invoices (PAGINATED)
# -------------------------
def get_all_invoices(limit=20, offset=0):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            source_file,
            bill_number,
            invoice_date,
            subtotal,
            tax_amount,
            grand_total,
            confidence,
            risk
        FROM invoices
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "source_file": r[0],
            "bill_number": r[1],
            "invoice_date": r[2],
            "subtotal": r[3],
            "tax_amount": r[4],
            "grand_total": r[5],
            "confidence": r[6],
            "risk": r[7]
        }
        for r in rows
    ]


# -------------------------
# Get High Risk Invoices (PAGINATED)
# -------------------------
def get_high_risk_invoices(limit=20, offset=0):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            source_file,
            bill_number,
            invoice_date,
            grand_total,
            confidence,
            risk
        FROM invoices
        WHERE risk = 'high'
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "source_file": r[0],
            "bill_number": r[1],
            "invoice_date": r[2],
            "grand_total": r[3],
            "confidence": r[4],
            "risk": r[5]
        }
        for r in rows
    ]
def get_invoices_by_risk(risk, limit=20, offset=0):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            source_file,
            bill_number,
            invoice_date,
            grand_total,
            confidence,
            risk
        FROM invoices
        WHERE risk = ?
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    """, (risk, limit, offset))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "source_file": r[0],
            "bill_number": r[1],
            "invoice_date": r[2],
            "grand_total": r[3],
            "confidence": r[4],
            "risk": r[5]
        }
        for r in rows
    ]
def get_invoices_by_date(start_date, end_date, limit=20, offset=0):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            source_file,
            bill_number,
            invoice_date,
            grand_total,
            confidence,
            risk
        FROM invoices
        WHERE invoice_date BETWEEN ? AND ?
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    """, (start_date, end_date, limit, offset))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "source_file": r[0],
            "bill_number": r[1],
            "invoice_date": r[2],
            "grand_total": r[3],
            "confidence": r[4],
            "risk": r[5]
        }
        for r in rows
    ]

def get_audit_logs(limit=50, offset=0):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            i.source_file,
            i.risk,
            i.confidence,
            r.reason
        FROM invoices i
        LEFT JOIN risk_explanations r
        ON i.id = r.invoice_id
        ORDER BY i.id DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))

    rows = cursor.fetchall()
    conn.close()

    audit_map = {}

    for source_file, risk, confidence, reason in rows:
        if source_file not in audit_map:
            audit_map[source_file] = {
                "source_file": source_file,
                "risk": risk,
                "confidence": confidence,
                "reasons": []
            }
        if reason:
            audit_map[source_file]["reasons"].append(reason)

    return list(audit_map.values())
