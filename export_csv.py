import json
import csv

with open("batch_output.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("output.csv", "w", newline="", encoding="utf-8") as f:
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

    for item in data:
        writer.writerow([
            item.get("source_file"),
            item.get("bill_number"),
            item.get("invoice_date"),
            item.get("subtotal"),
            item.get("tax_amount"),
            item.get("grand_total"),
            item["validation"]["total_match"]
        ])

print("CSV export complete → output.csv")
