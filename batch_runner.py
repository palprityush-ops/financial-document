import os
import json

from utils import clean_text
from extractor import extract_invoice_data
from validator import validate_totals

INPUT_DIR = "batch_texts"
OUTPUT_FILE = "batch_output.json"

results = []

# -------------------------
# Process each invoice file
# -------------------------
for file in os.listdir(INPUT_DIR):
    if not file.endswith(".txt"):
        continue

    file_path = os.path.join(INPUT_DIR, file)

    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    cleaned_text = clean_text(raw_text)

    extracted = extract_invoice_data(cleaned_text)

    total_valid = validate_totals(
        extracted["subtotal"],
        extracted["tax_amount"],
        extracted["grand_total"],
        extracted["issues"]
    )

    extracted["validation"] = {
        "total_match": total_valid,
        "issues": extracted["issues"]
    }

    extracted["source_file"] = file

    results.append(extracted)

# -------------------------
# Batch summary calculation
# -------------------------
total_invoices = len(results)

low_risk = 0
medium_risk = 0
high_risk = 0

total_confidence = 0
total_grand_amount = 0

for r in results:
    total_confidence += r.get("confidence", 0)

    if r.get("grand_total"):
        total_grand_amount += r["grand_total"]

    if r.get("risk_level") == "LOW":
        low_risk += 1
    elif r.get("risk_level") == "MEDIUM":
        medium_risk += 1
    elif r.get("risk_level") == "HIGH":
        high_risk += 1

batch_summary = {
    "total_invoices": total_invoices,
    "low_risk": low_risk,
    "medium_risk": medium_risk,
    "high_risk": high_risk,
    "average_confidence": round(
        total_confidence / total_invoices, 2
    ) if total_invoices > 0 else 0,
    "total_grand_amount": total_grand_amount
}

# -------------------------
# Final output
# -------------------------
final_output = {
    "invoices": results,
    "batch_summary": batch_summary
}

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(final_output, f, indent=4)

print("Batch processing complete. Output saved to", OUTPUT_FILE)
