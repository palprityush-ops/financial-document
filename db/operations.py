from db.database import get_connection


# -------------------------
# Insert Invoice
# -------------------------
def insert_invoice(invoice):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO invoices (
            source_file, bill_number, invoice_date,
            subtotal, tax_amount, grand_total,
            confidence, risk
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """,
        (
            invoice.get("source_file"),
            invoice.get("bill_number"),
            invoice.get("invoice_date"),
            invoice.get("subtotal"),
            invoice.get("tax_amount"),
            invoice.get("grand_total"),
            invoice.get("confidence"),
            invoice.get("risk"),
        ),
    )

    invoice_id = cursor.fetchone()["id"]

    for reason in invoice.get("risk_explanation", []):
        cursor.execute(
            """
            INSERT INTO risk_explanations (invoice_id, reason)
            VALUES (%s, %s)
        """,
            (invoice_id, reason),
        )

    conn.commit()
    cursor.close()
    conn.close()


# -------------------------
# Get All Invoices (PAGINATED)
# -------------------------
def get_all_invoices(limit=20, offset=0):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT source_file, bill_number, invoice_date,
               subtotal, tax_amount, grand_total, confidence, risk
        FROM invoices
        ORDER BY id DESC
        LIMIT %s OFFSET %s
    """,
        (limit, offset),
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(r) for r in rows]


# -------------------------
# Get High Risk Invoices
# -------------------------
def get_high_risk_invoices(limit=20, offset=0):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT source_file, bill_number, invoice_date,
               grand_total, confidence, risk
        FROM invoices
        WHERE risk = 'high'
        ORDER BY id DESC
        LIMIT %s OFFSET %s
    """,
        (limit, offset),
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(r) for r in rows]


# -------------------------
# Get Invoices by Risk
# -------------------------
def get_invoices_by_risk(risk, limit=20, offset=0):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT source_file, bill_number, invoice_date,
               grand_total, confidence, risk
        FROM invoices
        WHERE risk = %s
        ORDER BY id DESC
        LIMIT %s OFFSET %s
    """,
        (risk, limit, offset),
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(r) for r in rows]


# -------------------------
# Get Invoices by Date
# -------------------------
def get_invoices_by_date(start_date, end_date, limit=20, offset=0):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT source_file, bill_number, invoice_date,
               grand_total, confidence, risk
        FROM invoices
        WHERE invoice_date BETWEEN %s AND %s
        ORDER BY id DESC
        LIMIT %s OFFSET %s
    """,
        (start_date, end_date, limit, offset),
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(r) for r in rows]


# -------------------------
# Get Audit Logs
# -------------------------
def get_audit_logs(limit=50, offset=0):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT i.source_file, i.risk, i.confidence, r.reason
        FROM invoices i
        LEFT JOIN risk_explanations r ON i.id = r.invoice_id
        ORDER BY i.id DESC
        LIMIT %s OFFSET %s
    """,
        (limit, offset),
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    audit_map = {}
    for row in rows:
        row = dict(row)
        sf = row["source_file"]
        if sf not in audit_map:
            audit_map[sf] = {
                "source_file": sf,
                "risk": row["risk"],
                "confidence": row["confidence"],
                "reasons": [],
            }
        if row["reason"]:
            audit_map[sf]["reasons"].append(row["reason"])

    return list(audit_map.values())


# -------------------------
# Save New User
# -------------------------
def save_user(username, email, hashed_password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
        (username, email, hashed_password),
    )
    conn.commit()
    cursor.close()
    conn.close()


# -------------------------
# Get User by Username
# -------------------------
def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, email, password, role FROM users WHERE username = %s",
        (username,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return dict(row) if row else None
