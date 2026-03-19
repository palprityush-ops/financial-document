def calculate_risk_level(invoice):
    """
    Single invoice ka risk level calculate karo.
    Returns: 'low', 'medium', or 'high'
    """
    issues = 0

    if not invoice.get("grand_total"):
        issues += 2
    if not invoice.get("bill_number"):
        issues += 2
    if not invoice.get("invoice_date"):
        issues += 1
    if not invoice.get("subtotal"):
        issues += 1
    if not invoice.get("tax_amount"):
        issues += 1

    # Confidence check
    confidence = invoice.get("confidence", 1.0)
    if isinstance(confidence, (int, float)) and confidence < 0.5:
        issues += 2

    if issues >= 4:
        return "high"
    elif issues >= 2:
        return "medium"
    else:
        return "low"


def analyze_risk(batch_data):
    risk_distribution = {"low": 0, "medium": 0, "high": 0}

    for invoice in batch_data:
        risk = invoice["risk"]
        if risk in risk_distribution:
            risk_distribution[risk] += 1

    total_invoices = len(batch_data)
    high_risk_count = risk_distribution["high"]

    high_risk_percentage = (high_risk_count / total_invoices) * 100

    manual_review_required = False
    if high_risk_percentage > 20:
        manual_review_required = True

    return {
        "risk_distribution": risk_distribution,
        "high_risk_percentage": high_risk_percentage,
        "manual_review_required": manual_review_required,
    }