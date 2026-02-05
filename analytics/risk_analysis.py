def analyze_risk(batch_data):
    risk_distribution = {
        "low": 0,
        "medium": 0,
        "high": 0
    }

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
        "manual_review_required": manual_review_required
    }
