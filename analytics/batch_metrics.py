def calculate_batch_metrics(batch_data):
    amounts = []
    confidences = []

    for inv in batch_data:
        gt = inv.get("grand_total")
        if isinstance(gt, (int, float)):
            amounts.append(gt)

        conf = inv.get("confidence")
        if isinstance(conf, (int, float)):
            confidences.append(conf)

    total_amount = sum(amounts)
    total_invoices = len(batch_data)

    average_amount = round(
        total_amount / len(amounts), 2
    ) if amounts else 0

    average_confidence = round(
        sum(confidences) / len(confidences), 2
    ) if confidences else 0

    return {
        "total_invoices": total_invoices,
        "total_amount": total_amount,
        "average_amount": average_amount,
        "average_confidence": average_confidence
    }
