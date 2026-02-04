📄 Financial Document Analysis System (OCR-Based)
📌 Project Overview

Financial documents such as invoices are often available in unstructured text form after OCR processing.
Manual extraction and validation of such data is time-consuming and error-prone.

This project implements a rule-based Financial Document Analysis System that:

Extracts structured information from OCR invoice text

Performs financial validation checks

Processes invoices in batch

Generates structured JSON and CSV outputs

Assigns a confidence score to indicate data reliability

The system focuses on explainability and correctness, without relying on machine learning models.

🎯 Objectives

Extract key invoice fields (bill number, date, totals)

Extract line items (name, quantity, rate, total)

Handle OCR noise and missing values safely

Validate financial consistency:

Item total validation

Subtotal validation

Subtotal + tax = grand total validation

Generate structured outputs for analysis

🏗 System Architecture
OCR Invoice Text (.txt)
        ↓
Text Cleaning
        ↓
Regex-based Field Extraction
        ↓
Item-Level Extraction
        ↓
Validation Logic
        ↓
Confidence Scoring
        ↓
Structured Output (JSON / CSV)

📂 Project Structure
Mini project semester 4/
├── extractor.py
├── utils.py
├── ocr_test.py
├── batch_runner.py
├── export_csv.py
├── batch_texts/
│   ├── invoice1.txt
│   └── invoice2.txt
├── batch_output.json
├── output.csv
├── .gitignore
└── README.md

📄 File-wise Explanation
ocr_test.py

Used for testing extraction on a single invoice.

Reads OCR text

Cleans text

Extracts invoice data

Prints structured output

batch_runner.py

Main batch-processing engine.

Reads multiple invoice text files

Applies extraction and validation

Generates consolidated JSON output

Command:

python batch_runner.py

extractor.py

Core extraction and validation logic.

Extracts invoice header fields

Extracts item-level data

Validates:

Item totals

Subtotal consistency

Grand total consistency

Calculates confidence score

utils.py

Utility helper functions:

clean_text() → removes OCR noise

safe_value() → safely handles missing fields

export_csv.py

Converts JSON output into CSV format for Excel/audit use.

Command:

python export_csv.py

🔍 Validation Logic (Key Feature)

The system performs the following checks:

✔ Item-Level Validation
quantity × rate = item total

✔ Subtotal Validation
sum(item totals) = subtotal

✔ Grand Total Validation
subtotal + tax = grand total


Any mismatch is reported in the issues field.

📊 Confidence Scoring

A confidence score between 0.0 and 1.0 is assigned based on:

Missing invoice fields

Invalid item calculations

Financial mismatches

This score helps assess the reliability of OCR-extracted data.

▶️ How to Run
Single Invoice Test
python ocr_test.py

Batch Processing
python batch_runner.py

CSV Export
python export_csv.py

📄 Sample Output (JSON)
{
  "bill_number": "77821",
  "invoice_date": "12-08-2025",
  "subtotal": 98850,
  "tax_amount": 17793,
  "grand_total": 116643,
  "items": [
    {
      "name": "laptop dell inspiron",
      "qty": 2,
      "rate": 45500,
      "total": 91000,
      "calculated_total": 91000,
      "valid": true
    }
  ],
  "issues": [],
  "confidence": 0.9
}

⚠ Limitations

Works best with semi-structured invoice text

Regex-based extraction may fail on highly irregular formats

OCR accuracy directly affects results

🚀 Future Scope

NLP/ML-based entity extraction

Support for multiple invoice templates

Tax slab / GST analysis

Web interface or REST API

Database integration

✅ Conclusion

This project demonstrates a practical and explainable approach to financial document analysis.
By combining OCR text processing with rule-based validation, the system ensures accuracy, transparency, and auditability, making it suitable for academic and real-world use.


Note: Item names may contain extra text due to OCR noise.
This is a known limitation of rule-based extraction.
