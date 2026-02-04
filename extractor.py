import re
from utils import safe_value


def extract_items(cleaned_text):
    items = []

    item_pattern = re.compile(
        r'([a-z ]+?)\s+qty\s*(\d+)\s+rate\s*(\d+)\s+total\s*(\d+)',
        re.IGNORECASE
    )

    for name, qty, rate, total in item_pattern.findall(cleaned_text):
        qty = int(qty)
        rate = int(rate)
        total = int(total)

        calculated_total = qty * rate
        valid = (calculated_total == total)

        items.append({
            "name": name.strip(),
            "qty": qty,
            "rate": rate,
            "total": total,
            "calculated_total": calculated_total,
            "valid": valid
        })

    return items


def extract_invoice_data(cleaned_text):
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

    # Items
    items = extract_items(cleaned_text)

    # 🔥 ITEM vs SUBTOTAL VALIDATION (IMPORTANT)
    if items and subtotal is not None:
        items_sum = sum(item["total"] for item in items)
        if items_sum != subtotal:
            issues.append(
                f"Items total mismatch: items sum = {items_sum}, subtotal = {subtotal}"
            )

    # Confidence calculation
    confidence = 1.0

    for field in [bill_number, invoice_date, subtotal, tax_amount, grand_total]:
        if field is None:
            confidence -= 0.2

    # Penalize confidence if any item is invalid
    if any(not item["valid"] for item in items):
        confidence -= 0.2
        issues.append("One or more items have invalid totals")

    confidence = max(confidence, 0.0)

    return {
        "bill_number": bill_number,
        "invoice_date": invoice_date,
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "grand_total": grand_total,
        "items": items,
        "issues": issues,
        "confidence": round(confidence, 2)
    }
