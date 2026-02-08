import json
import csv
import os


def export_invoices_to_csv(
    batch_output_path="batch_output.json",
    output_csv_path="exports/invoices_export.csv"
):
    # Ensure export directory exists
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)

    # Load batch output
    with open(batch_output_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    invoices = data.get("invoices", [])

    # Write CSV
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            "source_file",
            "bill_number",
            "invoice_date",
            "subtotal",
            "tax_amount",
            "grand_total",
            "confidence",
            "risk_level",
            "total_match",
            "risk_explanation"
        ])

        # Rows
        for inv in invoices:
            writer.writerow([
                inv.get("source_file"),
                inv.get("bill_number"),
                inv.get("invoice_date"),
                inv.get("subtotal"),
                inv.get("tax_amount"),
                inv.get("grand_total"),
                inv.get("confidence"),
                inv.get("risk_level"),
                inv.get("validation", {}).get("total_match"),
                "; ".join(inv.get("risk_explanation", []))
            ])

    print("Invoice CSV export generated:", output_csv_path)
