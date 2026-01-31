import json
import csv

INPUT_JSON = "output.json"
OUTPUT_CSV = "output.csv"

with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

flat_data = {
    "bill_number": data.get("bill_number"),
    "invoice_date": data.get("invoice_date"),
    "subtotal": data.get("subtotal"),
    "tax_amount": data.get("tax_amount"),
    "grand_total": data.get("grand_total"),
    "total_match": data.get("validation", {}).get("total_match"),
    "issues": "; ".join(data.get("validation", {}).get("issues", []))
}

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=flat_data.keys())
    writer.writeheader()
    writer.writerow(flat_data)

print("output.csv generated successfully")
