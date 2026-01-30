# =========================
# Day 2–3: OCR Text Processing + Validation
# =========================

import re

# =========================
# STEP 1: Load raw OCR text
# =========================
with open("raw_ocr.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

print("\n===== RAW OCR TEXT =====\n")
print(raw_text)

# =========================
# STEP 2: Cleaning function
# =========================
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-z0-9\.\:\-/ ]', '', text)
    return text.strip()

cleaned_text = clean_text(raw_text)

print("\n===== CLEANED TEXT =====\n")
print(cleaned_text)

# =========================
# STEP 3: Information Extraction
# =========================

# Bill / Invoice Number
bill_no_match = re.search(
    r'(bill|invoice)\s*(no|number)?\s*[:\-]?\s*(\d+)',
    cleaned_text
)
bill_number = bill_no_match.group(3) if bill_no_match else None

# Date
date_match = re.search(r'(\d{2}[-/]\d{2}[-/]\d{4})', cleaned_text)
invoice_date = date_match.group(1) if date_match else None

# Grand Total
grand_total_match = re.search(
    r'(grand\s*total|total\s*amount\s*payable)\s*(\d+)',
    cleaned_text
)
grand_total = int(grand_total_match.group(2)) if grand_total_match else None

# =========================
# STEP 4: Extract Subtotal & Tax
# =========================
subtotal_match = re.search(r'sub\s*total\s*(\d+)', cleaned_text)
tax_match = re.search(r'tax\s*\d+\s*percent\s*(\d+)', cleaned_text)

subtotal = int(subtotal_match.group(1)) if subtotal_match else None
tax_amount = int(tax_match.group(1)) if tax_match else None

# =========================
# STEP 5: Validation Logic
# =========================
issues = []
total_valid = False

if subtotal is not None and tax_amount is not None and grand_total is not None:
    calculated_total = subtotal + tax_amount
    if abs(calculated_total - grand_total) <= 1:
        total_valid = True
    else:
        issues.append("Subtotal + tax does not match grand total")
else:
    issues.append("Missing values for validation")

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
