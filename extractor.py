def extract_invoice_data(cleaned_text):
    import re
    from utils import safe_value

    issues = []

    # Bill number
    bill_no_match = re.search(
        r'(bill|invoice)\s*(no|number)?\s*[:\-]?\s*(\d+)',
        cleaned_text
    )
    bill_number = safe_value(
        bill_no_match.group(3) if bill_no_match else None,
        "Bill number",
        issues
    )

    # Invoice date
    date_match = re.search(r'(\d{2}[-/]\d{2}[-/]\d{4})', cleaned_text)
    invoice_date = safe_value(
        date_match.group(1) if date_match else None,
        "Invoice date",
        issues
    )

    # Subtotal
    subtotal_match = re.search(r'sub\s*total\s*(\d+)', cleaned_text)
    subtotal = safe_value(
        int(subtotal_match.group(1)) if subtotal_match else None,
        "Subtotal",
        issues
    )

    # Tax amount
    tax_match = re.search(r'tax\s*\d+\s*percent\s*(\d+)', cleaned_text)
    tax_amount = safe_value(
        int(tax_match.group(1)) if tax_match else None,
        "Tax amount",
        issues
    )

    # Grand total
    grand_total_match = re.search(
        r'(grand\s*total|total\s*amount\s*payable)\s*(\d+)',
        cleaned_text
    )
    grand_total = safe_value(
        int(grand_total_match.group(2)) if grand_total_match else None,
        "Grand total",
        issues
    )

    # Confidence calculation
    confidence = 1.0

    if bill_number is None:
        confidence -= 0.2
    if invoice_date is None:
        confidence -= 0.2
    if subtotal is None:
        confidence -= 0.2
    if tax_amount is None:
        confidence -= 0.2
    if grand_total is None:
        confidence -= 0.2

    confidence = max(confidence, 0.0)

    return {
        "bill_number": bill_number,
        "invoice_date": invoice_date,
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "grand_total": grand_total,
        "issues": issues,
        "confidence": round(confidence, 2)
    }
