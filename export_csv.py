import csv
import json

def export_invoices_to_csv(
    batch_output_path="batch_output.json",
    output_csv_path="exports/invoices_export.csv"
):
    with open(batch_output_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    invoices = data.get("invoices", [])

    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "source_file",
            "bill_number",
            "invoice_date",
            "subtotal",
            "tax_amount",
            "grand_total",
            "total_match"
        ])

        for item in invoices:
            writer.writerow([
                item.get("source_file"),
                item.get("bill_number"),
                item.get("invoice_date"),
                item.get("subtotal"),
                item.get("tax_amount"),
                item.get("grand_total"),
                item.get("validation", {}).get("total_match")
            ])
