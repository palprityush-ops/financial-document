import re
import json

from utils import clean_text, safe_value
from extractor import extract_invoice_data
from validator import validate_totals



# =========================
# STEP 1: Load raw OCR text
# =========================

with open("raw_ocr.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

print("\n===== RAW OCR TEXT =====\n")
print(raw_text)

# =========================
# STEP 2: Clean text
# =========================

cleaned_text = clean_text(raw_text)

print("\n===== CLEANED TEXT =====\n")
print(cleaned_text)
extracted = extract_invoice_data(cleaned_text)

bill_number = extracted["bill_number"]
invoice_date = extracted["invoice_date"]
subtotal = extracted["subtotal"]
tax_amount = extracted["tax_amount"]
grand_total = extracted["grand_total"]
issues = extracted["issues"]

##
total_valid = validate_totals(
    subtotal,
    tax_amount,
    grand_total,
    issues
)
##

# =========================
# FINAL STRUCTURED OUTPUT
# =========================

final_result = {
    "bill_number": bill_number,
    "invoice_date": invoice_date,
    "subtotal": subtotal,
    "tax_amount": tax_amount,
    "grand_total": grand_total,
    "validation": {
        "total_match": total_valid,
        "issues": issues
    }
}

print("\n===== FINAL VALIDATED OUTPUT =====\n")
print(final_result)

# =========================
# SAVE TO JSON
# =========================

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(final_result, f, indent=4)

print("\noutput.json file generated successfully")
