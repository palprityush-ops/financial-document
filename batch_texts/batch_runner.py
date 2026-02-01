import os
import json

from process_text import clean_text
from extractor import extract_invoice_data
from validator import validate_totals

INPUT_DIR = "batch_texts"
OUTPUT_FILE = "batch_output.json"

all_results = []

for filename in os.listdir(INPUT_DIR):
    if not filename.endswith(".txt"):
        continue

    file_path = os.path.join(INPUT_DIR, filename)

    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    cleaned = clean_text(raw_text)

    extracted = extract_invoice_data(cleaned)

    total_valid, issues = validate_totals(
        extracted["subtotal"],
        extracted["tax_amount"],
        extracted["grand_total"]
    )

    extracted["validation"] = {
        "total_match": total_valid,
        "issues": issues
    }

    extracted["source_file"] = filename

    all_results.append(extracted)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=4)

print("Batch processing complete. Output saved to", OUTPUT_FILE)
