def calculate_batch_metrics(batch_data):
    total_invoices = len(batch_data)

    amounts = []
    for invoice in batch_data:
        amounts.append(invoice["total_amount"])

    total_amount = sum(amounts)
    min_invoice_value = min(amounts)
    max_invoice_value = max(amounts)
    average_invoice_value = total_amount / total_invoices

    return {
        "total_invoices": total_invoices,
        "total_amount": total_amount,
        "average_invoice_value": average_invoice_value,
        "min_invoice_value": min_invoice_value,
        "max_invoice_value": max_invoice_value
    }
