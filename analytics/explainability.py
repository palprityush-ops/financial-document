def explain_invoice_risk(invoice):
    reasons = []

    # Rule 1: Low confidence
    confidence = invoice.get("confidence")
    if isinstance(confidence, (int, float)) and confidence < 0.7:
        reasons.append("Low confidence score")

    # Rule 2: Validation failure
    if not invoice.get("validation", {}).get("total_match", True):
        reasons.append("Total mismatch detected")

    # Rule 3: No items detected
    items = invoice.get("items", [])
    if not items:
        reasons.append("No line items detected")

    # Rule 4: High amount heuristic (SAFE)
    total_amount = invoice.get("total_amount")
    if isinstance(total_amount, (int, float)) and total_amount > 100000:
        reasons.append("Unusually high invoice amount")

    # Default case
    if not reasons:
        reasons.append("No significant issues detected")

    return reasons
