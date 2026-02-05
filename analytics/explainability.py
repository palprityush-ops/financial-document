def explain_invoice_risk(invoice):
    reasons = []

    # Low confidence
    if invoice.get("confidence", 1) < 0.7:
        reasons.append("Low confidence score")

    # Validation failure
    if not invoice.get("validation", {}).get("total_match", True):
        reasons.append("Total mismatch detected")

    # No items detected
    if len(invoice.get("items", [])) == 0:
        reasons.append("No line items detected")

    # High amount heuristic (optional but impressive)
    if invoice.get("total_amount", 0) > 100000:
        reasons.append("Unusually high invoice amount")

    if not reasons:
        reasons.append("No significant issues detected")

    return reasons
