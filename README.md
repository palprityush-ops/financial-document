# Financial Document Analysis System (OCR-based)

##  Project Overview
This project extracts structured information from unstructured financial documents
(like invoices) using OCR and rule-based text processing.

The system converts invoice text into structured JSON data that can be
used for analysis and validation.

---

##  Objectives
- Extract key invoice fields (bill number, date, totals)
- Handle OCR noise and missing data safely
- Validate financial consistency (subtotal + tax = total)
- Generate structured JSON output

---

##  System Architecture

Raw Invoice Text  
↓  
Text Cleaning  
↓  
Field Extraction  
↓  
Validation Logic  
↓  
Structured JSON Output

---

##  Project Structure

Mini project semester 4/
├── ocr_test.py
├── utils.py
├── extractor.py
├── validator.py
├── raw_ocr.txt
├── output.json
├── invoices/
│   └── sample_invoices.pdf
├── .gitignore
└── README.md



---

##  File-wise Explanation

### ocr_test.py
Main entry point of the system.
Controls the complete workflow:
- Reads OCR text
- Cleans the text
- Extracts invoice fields
- Validates totals
- Saves output to JSON

---

### utils.py
Contains reusable helper functions:
- clean_text() → cleans OCR noise
- safe_value() → handles missing values safely

---

### extractor.py
Responsible for extracting invoice fields using regex:
- Bill number
- Invoice date
- Subtotal
- Tax amount
- Grand total

---

### validator.py
Contains business rules:
- Validates subtotal + tax against grand total
- Reports validation issues

---

## ▶️ How to Run

1. Activate virtual environment
2. Place OCR output in `raw_ocr.txt`
3. Run the main script:

```bash
python ocr_test.py



##The system generates a structured JSON output:

{
  "bill_number": "77821",
  "invoice_date": "12-08-2025",
  "subtotal": 98850,
  "tax_amount": 17793,
  "grand_total": 116643,
  "validation": {
    "total_match": true,
    "issues": []
  }}
