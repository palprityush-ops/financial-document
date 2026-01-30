# =========================
# Day 2: Text Processing
# =========================

import re

# STEP 1: Load raw OCR text from file
with open("raw_ocr.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

print("\n===== RAW OCR TEXT =====\n")
print(raw_text)


# STEP 2: Cleaning function
def clean_text(text):
    # convert to lowercase
    text = text.lower()

    # replace multiple spaces/newlines with single space
    text = re.sub(r'\s+', ' ', text)

    # keep only useful characters
    text = re.sub(r'[^a-z0-9\.\:\-/ ]', '', text)

    return text.strip()


# STEP 3: Apply cleaning
cleaned_text = clean_text(raw_text)

print("\n===== CLEANED TEXT =====\n")
print(cleaned_text)

# =========================
# STEP 3: Information Extraction
# =========================

# 1. Extract Invoice / Bill Number
bill_no_match = re.search(r'(bill|invoice)\s*(no|number)?\s*[:\-]?\s*(\d+)', cleaned_text)

bill_number = bill_no_match.group(3) if bill_no_match else None


# 2. Extract Date
date_match = re.search(r'(\d{2}[-/]\d{2}[-/]\d{4})', cleaned_text)

invoice_date = date_match.group(1) if date_match else None


# 3. Extract Grand Total Amount
total_match = re.search(
    r'(grand\s*total|total\s*amount\s*payable)\s*(\d+)',
    cleaned_text
)

grand_total = total_match.group(2) if total_match else None


# =========================
# FINAL STRUCTURED OUTPUT
# =========================

result = {
    "bill_number": bill_number,
    "invoice_date": invoice_date,
    "grand_total_amount": grand_total
}

print("\n===== EXTRACTED DATA =====\n")
print(result)
