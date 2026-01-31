import os
import json
from utils import clean_text
from extractor import extract_invoice_data
from validator import validate_totals

INPUT_DIR = "batch_texts"
OUTPUT_FILE = "batch_output.json"

results = []

for file in os.listdir(INPUT_DIR):
    if file.endswith(".txt"):
        with open(os.path.join(INPUT_DIR, file), "r", encoding="utf-8") as f:
            raw_text = f.read()

        cleaned = clean_text(raw_text)
        extracted = extract_invoice_data(cleaned)

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

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)

print("Batch processing complete")
