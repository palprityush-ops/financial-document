import json
import csv

INPUT_FILE = "batch_output.json"
OUTPUT_FILE = "items_output.csv"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    invoices = json.load(f)

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    writer.writerow([
        "bill_number",
        "invoice_date",
        "item_name",
        "quantity",
        "rate",
        "item_total",
        "calculated_total",
        "item_valid"
    ])

    for invoice in invoices:
        bill_number = invoice.get("bill_number")
        invoice_date = invoice.get("invoice_date")

        for item in invoice.get("items", []):
            writer.writerow([
                bill_number,
                invoice_date,
                item.get("name"),
                item.get("qty"),
                item.get("rate"),
                item.get("total"),
                item.get("calculated_total"),
                item.get("valid")
            ])

print("Item-level CSV exported to items_output.csv")
